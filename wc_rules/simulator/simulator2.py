from .utils import SimulationState, ActionQueue, Timer
from .writer import Writer
from ..matcher.core import ReteNet, default_rete_net_methods
from .scheduler import NextReactionMethod

from attrdict import AttrDict
from collections import ChainMap, deque

import inspect
from ..utils.data import NestedDict
from .utils import VariableDictionary

from ..utils.random import RandomIDXGenerator

class Simulator:

	default_matcher_methods = default_rete_net_methods
	default_scheduler = NextReactionMethod

	def __init__(self,model,data,timer_args={},writer=None):

		self.state = SimulationState()
		self.variables = VariableDictionary()
		self.matcher = self.default_matcher()
		self.timer = Timer(**timer_args)
		self.scheduler = self.default_scheduler()
		self.writer = writer if writer is not None else Writer()

		self.load_model(model,data)
		self.model = model
		self.data = data

	def default_matcher(self,methods=None):
		if methods is None:
			methods = self.default_matcher_methods
		net = ReteNet()
		for method in methods:
			net.configure(method)
		return net

	def load_model(self,model,data):
		self.matcher.initialize_start()
		self.matcher.initialize_end()
		for rname,rule in model.iter_rules():
			d = NestedDict.get(data,rname.split('.')[:-1])
			self.matcher.initialize_rule(rule, rname, d)
		return self

	def load_state(self,counts,seed=0):
		idxgen = RandomIDXGenerator(seed)
		for graph,num in counts:
			for action in graph.generate_actions(generator=idxgen,count=num):
				self.execute_primary_action(action)
		return self

	def execute_primary_action(self,action):
		tokens = action.execute(self.state)
		self.matcher.process(tokens)
		return self

	def show_matcher_configuration(self):
		return [x[0] for x in inspect.getmembers(self.matcher, predicate=inspect.ismethod)]

	def simulate(self):
		while True:
			rule, time = self.scheduler.pop()
			if rule is None or time > self.timer.end:
				break
			self.timer.update(time)
			tokens = self.fire(rule)
			self.matcher.update_tokens(tokens)
			self.writer.update(time)

		return self

	def fire(self,rule):
		rule_node = self.matcher.get_node(core=rule,type='rule')
		sample = self.matcher.function_sample_rule(rule)
		tokens = []
		for act in rule_node.data.actions:
			# an action is an ExecutableExpression
			if act.deps.declared_variable is not None:
				sample[act.deps.declared_variable] = act.exec(sample,rule_node.data.helpers)
			else:
				tokens += ActionQueue(act.exec(sample,rule_node.data.helpers)).execute(self.state)
		return tokens

	

		