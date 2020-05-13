
from collections import defaultdict
from .constraint import global_builtins
from pprint import pformat

class DependencyCollector:
	def __init__(self,deps):
		self.declared_variable = None
		self.attribute_calls = defaultdict(set)
		self.builtins = set()
		self.function_calls = defaultdict(dict)
		self.variables = set()
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
					kwpairs.add((kw,arg['variable']))
			self.function_calls[x['variable']]['function_name'] = dict(kws=kws,kwpairs=kwpairs)
		return self






