from obj_model import core
from .rule import RuleArchetype
from pprint import pformat

class RBM(core.Model):
	id = core.StringAttribute()
	children = core.OneToManyAttribute('RBM',related_name='parent')

	def __init__(self,id='',children=[],rules={},params={}):
		super().__init__()
		self.id=id
		self.children=children
		self.rules = rules
		self.params = params	

		
	def pprint_namespace(self):
		# in Python 3.8, sort_dicts=False to preserve insertion order
		namespace = {
			'id': self.id,
			'children': [c.id for c in self.children],
			'rules': [r for r in self.rules],
			'params': self.params
		}
		return pformat(namespace)	

	def validate(self):	
		assert isinstance(self.rules,dict), 'Rules in an RBM must be provided as a dictionary.'
		assert isinstance(self.params,dict), 'Params in an RBM must be provided as a dictionary.'

		required_params = set([param for x in self.rules.values() for param in x.params])
		for param in required_params:
			assert param in self.params, "Parameter '{0}' is required in this model.".format(param)
		super().validate()

	def add_rule(self,name,rule):
		assert isinstance(rule,RuleArchetype)
		self.rules[name] = rule
		return self

	def add_parameter(self,name,value):
		self.params[name]= value
		return self

	def all_nested_parameters(self):
		other_params = {m.id:m.nested_parameter_list() for m in self.children}
		self_params = self.params
		return {**self_params,**other_params}

