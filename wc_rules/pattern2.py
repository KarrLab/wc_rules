from .indexer import DictLike
from .utils import generate_id,ValidateError
from functools import partial
from .expr_new import process_constraint_strings
from .constraint import global_builtins
from functools import wraps

def matchset_method(fn):
	fn._is_matchset_method = True
	return fn

class Pattern(DictLike):

	def __init__(self,nodelist=[],recurse=True):
		super().__init__()
		self._constraints = []
		self._helpers = {}
		self._validated = False
		self._constraints = ''
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
		while len(deps) > 0:
			x = deps.pop(0)
			if isinstance(x,list):
				deps = x + deps
				continue
			assert isinstance(x,dict)
			print(x)
			v,a,f,p,n = None,None,None,None,None
			is_node,is_helper = False,False
			if 'declared_variable' in x:
				v = x['declared_variable']
				assert v not in declared_variables, "Cannot reuse variable name '{v}'".format(v=v)
				assert v not in self._dict, "Cannot reuse variable name '{v}'".format(v=v)
				assert v not in self._helpers, "Cannot reuse variable name '{v}'".format(v=v)
				declared_variables.append(x['declared_variable'])
			if 'variable' in x:
				v = x['variable']
				is_node = v in self._dict
				is_helper = v in self._helpers
				is_declared = v in declared_variables
				assert is_node or is_helper or is_declared, "Variable '{v}' not found!".format(v=v)
			if 'attribute' in x:
				a = x['attribute']
				if is_node:
					err = 'Attribute {a} not found!'.format(a=a)
				elif is_helper:
					err = "Improper function call '{a}' on helper '{v}'!".format(v=v,a=a)
				assert is_node and a in self[v].get_literal_attrs(),err
			if 'function_name' in x:
				f = x['function_name']
				if v is None:
					assert f in global_builtins, "Function call '{f}' not a valid builtin!".format(f=f)
				if is_helper:
					p = self._helpers[v]
					assert getattr(p,f,False), "Helper function call '{v}.{f}' not a valid function!".format(f=f,v=v)
					assert getattr(getattr(p,f),'_is_matchset_method',False), "Helper function call '{v}.{f}' not a valid function!".format(f=f,v=v)
					if 'kws' in x:
						assert set(x['kws']).issubset(set(p.keys())), "Helper function call '{v}.{f}' can only use keywords from variable names in helper pattern".format(f=f,v=v)
				if is_node:
					n = self[v]
					assert getattr(n,f,False), "Function call '{v}.{f}' not a valid local compute function!".format(f=f,v=v)
					assert getattr(getattr(n,f),'_is_local_compute',False), "Function call '{v}.{f}' not a valid local compute function!".format(f=f,v=v)
					if 'kws' in x:
						assert set(x['kws']).issubset(set(getattr(getattr(n,f),'_args',False))), "Local compute function call '{v}.{f}' can only use specified keywords!".format(f=f,v=v)
				if 'args' in x:
					deps = x['args'] + deps
		self._validated = True		


	@matchset_method
	def count(self,**kwargs):
		return 0

	def contains(self,**kwargs):
		return False
