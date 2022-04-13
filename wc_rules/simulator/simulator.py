from ..matcher.core import build_rete_net_class
from .scheduler import NextReactionMethod
from ..utils.collections import DictLike, LoggableDict
from ..utils.data import NestedDict
from ..modeling.model import AggregateModel
from collections import defaultdict

def get_model_name(rule_name):
	return '.'.join(rule_name.split('.')[:-1])

class Simulator:

	ReteNetClass = build_rete_net_class()
	Scheduler = NextReactionMethod

	def __init__(self,model=None,parameters=None,**kwargs):
		
		model.verify(parameters)
		self.parameters = NestedDict.flatten(parameters)
		self.rules = dict(model.iter_rules())
		self.parameter_dependencies = defaultdict(list)

		for r,rule in self.rules.items():
			for p in rule.parameters:
				self.parameter_dependencies[r].append(f'{get_model_name(r)}.{p}')

		self.net = self.ReteNetClass() \
			.initialize_start() \
			.initialize_end()	\
			.initialize_rules(self.rules,self.parameters)


		





