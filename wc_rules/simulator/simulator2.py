from .utils import SimulationState, ActionQueue, Timer
from .writer import Writer
from ..matcher.core import ReteNet, default_rete_net_methods
from .scheduler import NextReactionMethod

from attrdict import AttrDict
from collections import ChainMap, deque
from types import MethodType
import inspect


class Simulator:

	default_matcher_methods = default_rete_net_methods
	default_scheduler = NextReactionMethod

	def __init__(self,matcher=None,scheduler=None,timer_args={},writer=None):

		self.state = SimulationState()
		self.matcher = ReteNet() if matcher is None else matcher
		self.timer = Timer(**timer_args)
		self.scheduler = scheduler if scheduler is not None else NextReactionMethod()
		self.writer = writer if writer is not None else Writer()

		self.configure_matcher()
		
	def configure_matcher(self,methods=None,overwrite=True):
		methods = self.default_matcher_methods if methods is None else methods
		for method in methods:
			m = MethodType(method, self.matcher)
			assert overwrite or method.__name__ not in dir(self.matcher)
			setattr(self.matcher,method.__name__,m)	
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

	

		