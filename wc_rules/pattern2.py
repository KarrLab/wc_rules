from .indexer import DictLike
from .utils import generate_id,ValidateError,listmap
from functools import partial
from .expr_new import process_constraint_string
from .constraint import global_builtins
from functools import wraps
from .entity import Entity
from pprint import pformat
from collections import defaultdict

class Scaffold(DictLike):
	# scaffold, a graph with nodes and edges
	# nodes have all literal attrs set to None,except id attribute
	# namespace of scaffold = ids of nodes
	def __init__(self,node):
		assert isinstance(node,Entity), "Scaffold can only be initialized from some node of an entity graph."
		super().__init__()
		self.__add_node(node)
		
	def __add_node(self,node):
		# always recurse through graph and add everything
		for attr in node.get_literal_attrs().keys():
			if attr == 'id':
				continue
			assert getattr(node,attr) is None, "Scaffold should not have attributes."
		if node in self:
			return self
		self.add(node)	
		for new_node in node.listget_all_related():
			self.__add_node(new_node)
		return self

	def get_namespace(self,as_string=False):
		if as_string:
			return pformat(self.get_namespace())
		return {x:x.__class__ for i,x in self._dict.items()}

def helperfn(fn):
	fn._is_helperfn = True
	return fn
		
class Pattern:

	def __init__(self,scaffold,helpers=dict(),constraints=''):
		assert isinstance(scaffold,Scaffold), "Scaffold keyword argument must be a scaffold."
		assert isinstance(helpers,dict), "Helpers keyword argument must be a dict."
		assert isinstance(constraints,str), "Constraints keyword argument must be a str."
		self.scaffold = scaffold
		self.variables = scaffold.keys()
		
		self.helpers = dict()
		self.constraints = []
		self.declared_variables = []

		self.add_helpers(helpers)
		self.add_constraints(constraints)
		

	def add_helpers(self,_dict):
		for variable,pattern in _dict.items():
			assert variable not in self.variables and variable not in self.declared_variables, 'Variable {v} already exists in this pattern.'.format(v=variable)
			assert pattern not in self.helpers.values(), 'Pattern added to variable {v} has already been added as a helper.'.format(v=variable)
			assert pattern is not self, 'Cannot add a pattern as its own helper.'
			self.helpers[variable] = pattern
		return self

	def get_namespace(self,as_string=False):
		if as_string:
			return pformat(self.get_namespace())
		return {'scaffold':self.scaffold.get_namespace(),
		'helpers':self.helpers,
		'declared_variables':self.declared_variables,
		'constraints':self.constraints
		}

	def add_constraints(self,string_input):
		strings = listmap(str.strip,string_input.split('\n'))
		

		for string in strings:
			if len(string)==0:
				continue
			tree,deps = process_constraint_string(string)
			d = DependencyCollector(deps)
			print(d.to_string())
			errs = d.validate(self)
			assert len(errs)==0, "Errors found in pattern definition.\n "+ '\n '.join(errs)
			d.modify(self)
			
		return self
	
	@helperfn
	def count(self,**kwargs):
		return None

	@helperfn
	def contains(self,**kwargs):
		return None



class DependencyCollector:
	def __init__(self,deps):
		self.declared_variable = None
		self.attribute_calls = defaultdict(set)
		self.builtins = set()
		self.function_calls = defaultdict(dict)
		self.variables = set()
		self.errors = []
		self.collect_dependencies(deps)

	def to_string(self):
		attrs = ['declared_variable','attribute_calls','builtins','function_calls','variables']
		return pformat({attr:getattr(self,attr) for attr in attrs})
		
	def collect_dependencies(self,deps):
		while len(deps)>0:
			x = deps.pop(0)
			if x is None:
				continue
			if isinstance(x,list):
				deps = x + deps
				continue
			assert isinstance(x,dict)
			self.process(x)
			if 'args' in x:
				deps = x['args'] + deps
		return self

	def process(self,x):
		self.process_declared_variable(x)
		self.process_variable(x)
		self.process_builtin(x)
		self.process_attribute_call(x)
		self.process_function_call(x)
		return 

	def process_declared_variable(self,x):
		if 'declared_variable' in x:
			self.declared_variable = x['declared_variable']
		return self

	def process_variable(self,x):
		if 'variable' in x:
			self.variables.add(x['variable'])
		return self

	def process_builtin(self,x):
		if 'function_name' in x and 'variable' not in x:
			self.builtins.add(x['function_name'])
		return self

	def process_attribute_call(self,x):
		if 'attribute' in x:
			self.attribute_calls[x['variable']].add(x['attribute'])
		return self

	def process_function_call(self,x):
		if 'function_name' in x and 'variable' in x:
			kws = set()
			if 'kws' in x:
				kws = set(x['kws'])
			kwpairs = set()
			for i,kw in enumerate(kws):
				arg = x['args'][i]
				if isinstance(arg,dict) and len(arg.keys())==1 and 'variable' in arg:
					kwpairs.add((kw,x['variable']))
			self.function_calls[x['variable']]['function_name'] = dict(kws=kws,kwpairs=kwpairs)
		return self

	def validate(self,pattern):
		# don't modify the pattern, just query it, validate and collect errors
		errs = []
		return errs

	def modify(self,pattern):
		# incorporate changes into pattern
		return self












class Bla:

	def validate_variable(self,x):
		pattern = self.pattern
		v = x['variable']
		condition = v in pattern.variables or v in pattern.helpers or v in pattern.declared_variables
		if condition==False:
			return ["Variable '{v}' not found.".format(v=v)]
		return []
		
	def validate_declared_variable(self,x):
		v = x['declared_variable']
		pattern = self.pattern
		condition = v not in pattern.variables and v not in pattern.helpers and v not in pattern.declared_variables
		if condition == False:
			return ["Cannot reuse variable name '{v}'.".format(v=v)]
		pattern.declared_variables.append(v)
		return []

	def validate_attribute(self,x):
		v,a = [x[y] for y in ['variable','attribute']]
		pattern = self.pattern
		condition = (v in pattern.variables and a in pattern.scaffold[v].get_literal_attrs()) or v in pattern.declared_variables
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
		pattern = self.pattern
		fn = getattr(pattern.scaffold[v],f,False)
		condition = fn and fn._is_localfn
		if condition == False:
			return ["Function '{v}.{f}()' is not a valid local function.".format(f=f,v=v)]
		if 'kws' in x:
			for kw in x['kws']:
				condition = kw in fn._args
				if condition == False:
					return ["'Keyword '{kw}'' not a variable in namespace of local function '{v}.{f}()'".format(v=v,f=f,kw=kw)]
		return []

	def validate_helper_function(self,x):
		f,p = [x[y] for y in ['function_name','variable']]
		pat = self.pattern.helpers[p]
		fn = getattr(pat,f,False)
		condition = fn and fn._is_helperfn
		if condition == False:
			return ["'{p}.{f}()' is not a valid helper function.".format(p=p,f=f)]
		if 'kws' in x:
			for kw in x['kws']:
				condition = kw in pat.variables or kw in pat.declared_variables
				if condition == False:
					return ["'Keyword '{kw}'' not a variable in namespace of helper pattern '{p}'".format(p=p,kw=kw)]
		return []