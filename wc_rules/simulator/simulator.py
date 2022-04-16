from ..matcher.core import build_rete_net_class
from .scheduler import NextReactionMethod
from ..utils.collections import DictLike, LoggableDict
from ..utils.data import NestedDict
from ..modeling.model import AggregateModel
from collections import defaultdict, deque
from attrdict import AttrDict
from ..schema.actions import PrimaryAction
from ..matcher.token import convert_action_to_tokens

def get_model_name(rule_name):
	return '.'.join(rule_name.split('.')[:-1])

class ActionStack:

	def __init__(self,cache):
		self._dq  = deque()
		self.cache = cache

	def put(self,action):
		if isinstance(action,list):
			self._dq.extend(action)
		else:
			self._dq.append(action)
		return self

	def put_first(self,action):
		if isinstance(action,list):
			self._dq.extend(reversed(action))
		else:
			self._dq.appendleft(action)
		return self

	def do(self):
		tokens = []
		while self._dq:
			x = self._dq.popleft()
			if isinstance(x,PrimaryAction):
				x.execute(self.cache)
				tokens.extend(convert_action_to_tokens(x,self.cache))
			elif isinstance(x,CompositeAction):
				self.put_first(x.expand())
		return tokens

class SimulationEngine:

	ReteNetClass = build_rete_net_class()
	Scheduler = NextReactionMethod

	def __init__(self,model=None,parameters=None,**kwargs):
		
		model.verify(parameters)
		self.parameters = NestedDict.flatten(parameters)
		self.rules = dict(model.iter_rules())
		self.parameter_dependencies = defaultdict(list)
		self.cache = DictLike()

		for r,rule in self.rules.items():
			for p in rule.parameters:
				self.parameter_dependencies[r].append(f'{get_model_name(r)}.{p}')

		self.net = self.ReteNetClass() \
			.initialize_start() \
			.initialize_end()	\
			.initialize_rules(self.rules,self.parameters)

	def load(self,objects):
		# object must have an iterator object.generate_actions()
		ax = ActionStack(self.cache)
		start = self.net.get_node(type='start')
		for x in objects:
			for action in x.generate_actions():
				tokens = ax.put(action).do()
				self.net.process_tokens(tokens)
		return self

			





	