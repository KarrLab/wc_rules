from .indexer import DictLike
from .utils import generate_id,ValidateError
from functools import partial
from .expr_new import process_constraint_strings
from .constraint import global_builtins
from functools import wraps

def helperfn(fn):
	fn._is_helperfn = True
	return fn

class Pattern(DictLike):

	def __init__(self,nodelist=[],recurse=True):
		super().__init__()
		self._constraints = ''
		self._helpers = {}
		self._declared_variables = []	
		self._validated = False

		for node in nodelist:
			self.add_node(node)

        
	def add_node(self,node):
		# always recurse through graph and add everything
		if node in self:
			return self
		self.add(node)	
		for new_node in node.listget_all_related():
			self.add_node(new_node)

		for node in self:
			n = node.get_id()
			for a in node.get_nonempty_scalar_attributes():
				v = getattr(node,a)
				if isinstance(v,str):
					v = '"{v}"'.format(v=v) 
				self._constraints += '{n}.{a} == {v}\n'.format(n=n,a=a,v=v)

		return self

	def add_helpers(self,_dict):
		for variable,pattern in _dict.items():
			assert variable not in self._dict, 'A variable with this name already exists in the pattern'
			assert pattern not in self._helpers.values(), 'A pattern with this name has already been added as a helper.'
			assert pattern is not self, 'Cannot add a pattern as its own helper.'
			self._helpers[variable] = pattern
		return self

	def add_constraints(self,string_input):
		self._constraints += string_input
		return self

	def validate_dependencies(self):
		tree,deps = process_constraint_strings(self._constraints)
		declared_variables = []
		errs = []
		while len(deps) > 0:
			x = deps.pop(0)
			if isinstance(x,list):
				deps = x + deps
				continue
			assert isinstance(x,dict)			
			if 'declared_variable' in x:
				errs += self.validate_declared_variable(x)
			if 'variable' in x:
				errs += self.validate_variable(x)
			if 'attribute' in x:
				errs += self.validate_attribute(x)
			if 'function_name' in x:
				if 'variable' not in x:
					errs += self.validate_builtin(x)
				elif x['variable'] in self._helpers:
					errs += self.validate_helper_function(x)
				elif x['variable'] in self._dict:
					errs += self.validate_local_function(x)

		assert len(errs)==0, '\n\nThe following validation errors were found:\n\t'+'\n\t'.join(errs)
		self._validated = True
		return True

	def validate_variable(self,x):
		v = x['variable']
		condition = v in self._dict or v in self._helpers or v in self._declared_variables
		if condition==False:
			return ["Variable '{v}' not found.".format(v=v)]
		return []
		
	def validate_declared_variable(self,x):
		v = x['declared_variable']
		condition = v not in self._dict and v not in self._helpers and v not in self._declared_variables
		if condition == False:
			return ["Cannot reuse variable name '{v}'.".format(v=v)]
		self._declared_variables.append(v)
		return []

	def validate_attribute(self,x):
		v,a = [x[y] for y in ['variable','attribute']]
		condition = (v in self._dict and a in self[v].get_literal_attrs()) or v in self._declared_variables
		if condition == False:
			return ["Could not validate attribute '{v}.{a}'".format(v=v,a=a)]
		return []

	def validate_builtin(self,x):
		f = x['function_name']
		condition = f in global_builtins
		if condition == False:
			return ["Builtin '{f}()' not found in list of approved builtins.".format(f=f)]
		return []

	def validate_local_function(self,x):
		v,f = [x[y] for y in ['variable','function_name']]
		fn = getattr(self[v],f,False)
		condition = fn and fn._is_localfn
		if condition == False:
			return ["Function '{v}.{f}()' is not a valid local function.".format(f=f,v=v)]
		if 'kws' in x:
			condition = set(x['kws']).issubset(set(getattr(self[v],'_args')))
			if condition == False:
				return ["Function '{v}.{f}()' only takes keywords specified in the function definition.".format(f=f,v=v)]
		return []

	def validate_helper_function(self,x):
		f,p = [x[y] for y in ['function_name','variable']]
		pat = self._helpers[p]
		fn = getattr(pat,f,False)
		condition = fn and fn._is_helperfn
		if condition == False:
			return ["'{p}.{f}()' is not a valid helper function.".format(p=p,f=f)]
		if 'kws' in x:
			condition = set(x['kws']).issubset(set(pat.keys()))
			if condition == False:
				return ["'{p}.{f}' can only use keyword arguments specified as variables in '{p}'".format(p=p,f=f)]
		return []

	@helperfn
	def count(self,**kwargs):
		return 0

	@helperfn
	def contains(self,**kwargs):
		return False
