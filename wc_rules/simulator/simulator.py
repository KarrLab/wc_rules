from ..matcher.core import build_rete_net_class
from .scheduler import NextReactionMethod
from ..utils.collections import DictLike, LoggableDict, subdict
from ..utils.data import NestedDict
from ..modeling.model import AggregateModel
from collections import defaultdict, deque, ChainMap
from attrdict import AttrDict
from ..schema.actions import PrimaryAction, CompositeAction
from ..matcher.token import convert_action_to_tokens
from ..expressions.executable import ActionManager

def get_model_name(rule_name):
	return '.'.join(rule_name.split('.')[:-1])

class ActionStack:

	def __init__(self,cache):
		self._dq  = deque()
		self.cache = cache
		self.record = deque()

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
				self.record.append(x)
				tokens.extend(convert_action_to_tokens(x,self.cache))
			elif isinstance(x,CompositeAction):
				self.put_first(x.expand())
		return tokens

class SimulationEngine:

	ReteNetClass = build_rete_net_class()
	Scheduler = NextReactionMethod

	def __init__(self,model=None,parameters=None,**kwargs):
		
		model.verify(parameters)
		self.parameters = LoggableDict(NestedDict.flatten(parameters))
		self.rules = dict(model.iter_rules())
		self.action_managers = {rule_name:ActionManager(rule.get_action_executables()) for rule_name,rule in self.rules.items()}
		self.cache = DictLike()

		self.net = self.ReteNetClass() \
			.initialize_start() \
			.initialize_end()	\
			.initialize_rules(self.rules,self.parameters)

		for node in self.net.get_nodes(type='variable'):
			self.parameters.set(node.core,node.state.cache.value)

	def get_updated_variables(self):
		modified = list(self.parameters.modified)
		self.parameters.flush()
		return modified

	def load(self,objects):
		# object must have an iterator object.generate_actions()
		ax = ActionStack(self.cache)
		start = self.net.get_node(type='start')
		for x in objects:
			for action in x.generate_actions():
				tokens = ax.put(action).do()
				self.net.process_tokens(tokens)
		for variable in self.net.get_updated_variables():
			value = self.net.get_node(core=variable).state.cache.value
			self.parameters.set(variable,value)
		return self

	def fire(self,rule_name):
		
		rule = self.rules[rule_name]
		match = {reactant: AttrDict(self.net.get_node(core=pattern).state.cache.sample()) for reactant,pattern in rule.reactants.items()}
		model_name = get_model_name(rule_name)
		parameters = {p:self.parameters[f'{model_name}.{p}'] for p in rule.parameters}
		action_manager = self.action_managers[rule_name]
		ax = ActionStack(self.cache)
		for action in action_manager.exec(match,parameters):
			tokens = ax.put(action).do()
			self.net.process_tokens(tokens)
		for variable in self.net.get_updated_variables():
			value = self.net.get_node(core=variable).state.cache.value
			self.parameters.set(variable,value)
		return self






