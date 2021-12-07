from .rule import Rule
from .observable import Observable
from ..utils.validate import *
from ..utils.collections import DictLike,merge_lists
from collections.abc import Sequence

def add_prefix(prefix,name):
	if prefix:
		return f'{prefix}.{name}'
	return name

class RuleBasedModel:

	defaults = None

	def __init__(self,name,rules,observables=[]):
		validate_keywords([name],'Model name')
		self.name = name

		validate_list(rules,Rule,'Rule')
		rule_names = [x.name for x in rules]
		validate_set(rule_names,'Rule names in a model')
		self.rules = rules
		validate_list(observables,Observable,'Observable')
		self.observables = observables
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

	def iter_rules(self,prefix=''):
		for rule in self.rules:
			yield add_prefix(prefix,rule.name), rule

	def iter_observables(self,prefix=''):
		for observable in self.observables:
			yield add_prefix(prefix,observable.name), observable

			


class AggregateModel:

	defaults = None

	def __init__(self,name,models,observables=[]):
		validate_keywords([name],'Model name')
		self.name = name

		validate_list(models,(RuleBasedModel,AggregateModel),'Model')
		model_names =  [x.name for x in models]
		validate_set(model_names,'Model names in an aggregate model')
		self.models = models
		validate_list(observables,Observable,'Observable')
		self.observables = observables
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
		
	def iter_models(self,prefix=''):
		for m in self.models:
			n = add_prefix(prefix,m.name) 
			yield n,m 
			if hasattr(m,'iter_models'):
				for n1,m1 in m.iter_models(prefix=n):
					yield n1,m1

	def iter_rules(self,prefix=''):
		for n,m in self.iter_models(prefix):
			if hasattr(m,'rules'):
				for n1,r1 in m.iter_rules(prefix=n):
					yield n1,r1

	def iter_observables(self,prefix=''):
		for observable in self.observables:
			yield add_prefix(prefix,observable.name), observable
		for n,m in self.iter_models(prefix):
			yield from m.iter_observables()


