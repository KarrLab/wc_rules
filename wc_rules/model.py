from .rule import Rule
from .validate_helpers import *
from .utils import merge_lists
from .indexer import DictLike
from pprint import pformat

class RuleBasedModel:

	def __init__(self,name,rules):
		validate_keywords([name],'Model name')
		self.name = name

		validate_list(rules,Rule,'Rule')
		rule_names = [x.name for x in rules]
		validate_set(rule_names,'Rule names in a model')
		self.rules = rules
		self._dict = {x.name:x for x in self.rules}

	def verify(self,data):
		for rule in self.rules:
			validate_contains(data.keys(),rule.params,'Parameter')

	@property
	def namespace(self):
		return {x.name: x.__class__.__name__ for x in self.rules}

	def required_parameters(self):
		params = []
		for x in self.rules:
			for p in x.params:
				if p not in params:
					params.append(p)
		return params

	def __getattr__(self,name):
		try:
			out = object.__getattr__(self,name)
		except:
			try:
				out = self._dict[name]
			except:
				raise AttributeError(f'{self.__class__.__name__}.{name} is not a valid attribute or contained rule.')
		return out

	def visualize_structure(self,count=0):
		return '\n'.join( [count*'  ' + self.name] + [(count+1)*'  ' + x.name for x in self.rules] )

	def visualize_params(self,count=0):
		return '\n'.join( [count*'  ' + self.name] + [(count+1)*'  ' + x for x in self.required_parameters()] )			

class AggregateModel:

	def __init__(self,name,models):
		validate_keywords([name],'Model name')
		self.name = name

		validate_list(models,(RuleBasedModel,AggregateModel),'Model')
		model_names =  [x.name for x in models]
		validate_set(model_names,'Model names in an aggregate model')
		self.models = models
		self._dict = {x.name:x for x in self.models}

	def verify(self,data):

		for model in self.models:
			model.verify(data.get(model.name,{}))

	@property
	def namespace(self):
		return {x.name: x.__class__.__name__ for x in self.models}

	def __getattr__(self,name):
		try:
			out = object.__getattr__(self,name)
		except:
			try:
				out = self._dict[name]
			except:
				raise AttributeError(f'{self.__class__.__name__}.{name} is not a valid attribute or contained model.')
		return out

	def visualize_structure(self,count=0):
		return '\n'.join( [count*'  ' + self.name] + [x.visualize_structure(count+1) for x in self.models] )
	
	def visualize_params(self,count=0):
		return '\n'.join( [count*'  ' + self.name] + [x.visualize_params(count+1) for x in self.models] )	