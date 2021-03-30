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


	def verify(self,data):
		for rule in self.rules:
			validate_contains(data.keys(),rule.params,'Parameter')

	@property
	def namespace(self):
		return {x.name: x.__class__.__name__ for x in self.rules}

	def required_parameters(self):
		return list(set(merge_lists([x.params for x in self.rules])))

	def __getattr__(self,name):
		try:
			object.__getattr__(self,name)
		except:
			assert name in [x.name for x in self.rules], "Could not find rule `{0}` in this RuleBasedModel.".format(name)
			return [x for x in self.rules if x.name==name][0]


class AggregateModel:

	def __init__(self,name,models):
		validate_keywords([name],'Model name')
		self.name = name

		validate_list(models,(RuleBasedModel,AggregateModel),'Model')
		model_names =  [x.name for x in models]
		validate_set(model_names,'Model names in an aggregate model')
		self.models = models

	def verify(self,data):

		for model in self.models:
			model.verify(data.get(model.name,{}))

	@property
	def namespace(self):
		return {x.name: x.__class__.__name__ for x in self.models}

	def __getattr__(self,name):
		try:
			object.__getattr__(self,name)
		except:
			assert name in [x.name for x in self.models], "Could not find model `{0}` in this AggregateModel.".format(name)
			return [x for x in self.models if x.name==name][0]

	