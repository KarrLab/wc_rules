from .rule import Rule
from ..utils.validate import *
from ..utils.collections import DictLike,merge_lists
from collections.abc import Sequence

class RuleBasedModel:

	defaults = None

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
			validate_contains(data.keys(),rule.parameters,'Parameter')
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

	def collect_parameters(self):
		assert self.defaults is not None, "Model has no default parameters."
		self.verify(self.defaults)
		return self.defaults

	def collect_rules(self):
		return [rule.name for rule in self.rules]

	def get_rule(self,name):
		if isinstance(name,str):
			return [x for x in self.rules if x.name == name][0]
		assert isinstance(name,(tuple,list)) and isinstance(name[0],str)
		return self.get_rule(name[0])


class AggregateModel:

	defaults = None

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

	def collect_parameters(self):
		if self.defaults is None:
			return {model.name: model.collect_parameters() for model in self.models}
		else:
			self.verify(self.defaults)
			return self.defaults

	def collect_rules(self):
		return {model.name: model.collect_rules() for model in self.models}

	def get_model(self,name):
		return [x for x in self.models if x.name==name][0]

	def get_rule(self,path):
		if isinstance(path,str):
			path = path.split('.')
		return self.get_model(path[0]).get_rule(path[1:])
		
	def iter_models(self):
		for m in self.models:
			yield m.name, m
			if hasattr(m,'iter_models'):
				for n1,m1 in m.iter_models():
					yield n1,m1


