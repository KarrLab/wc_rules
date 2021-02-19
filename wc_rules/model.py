from .rule import RuleArchetype
from pprint import pformat

class RuleBasedModel:

	def __init__(self,name):
		assert isinstance(name,str)
		self.name = name
		self.children = []
		self.rules = {}
		self.params = {}

	def add_rule(self,name,rule):
		assert isinstance(name,str)
		assert isinstance(rule,RuleArchetype)
		self.rules[name]=rule
		return self

	def add_param(self,name,param):
		assert isinstance(name,str)
		self.params[name]=param
		return self

	def add_child(self,child):
		assert isinstance(child,self.__class__)
		self.children.append(child)
		return self

	def validate(self):
		required_params = set([p for r in self.rules.values() for p in r.params])
		for p in required_params:
			assert p in self.params
		childnames = set([c.name for c in self.children])
		assert len(childnames) == len(self.children)

	def pprint_namespace(self):
		d = {
		'name': self.name,
		'children': [x.name for x in self.children],
		'rules': self.rules,
		'params': self.params
		}
		return pformat(d)

	def all_nested_parameters(self):
		d = {self.name:self.params}
		for c in self.children:
			d[self.name].update(c.all_nested_parameters())
		return d

	def pprint_nested_parameters(self):
		return pformat(self.all_nested_parameters())
