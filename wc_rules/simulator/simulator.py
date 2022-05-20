from ..matcher.core import build_rete_net_class
from .scheduler import NextReactionMethod, PeriodicWriteObservables,CoordinatedScheduler
from ..utils.collections import DictLike, LoggableDict, subdict
from ..utils.data import NestedDict
from ..modeling.model import AggregateModel
from collections import defaultdict, deque, ChainMap
from collections.abc import Sequence
from attrdict import AttrDict
from ..schema.actions import PrimaryAction, CompositeAction, RemoveNode, CollectReferences
from ..matcher.token import convert_action_to_tokens
import sys

def get_model_name(rule_name):
	return '.'.join(rule_name.split('.')[:-1])

class PrefixSubdict:

	def __init__(self,prefix,target):
		self.prefix = prefix
		self.target = target

	def __contains__(self,key):
		return f'{self.prefix}.{key}' in self.target

	def __getitem__(self,key):
		return self.target[f'{self.prefix}.{key}']

CURRENT_ACTION_RECORD = deque()

class ActionStack:

	def __init__(self,cache,match):
		self._dq  = deque()
		self.cache = cache
		self.match = match
		self.record = deque()

	def put(self,action):
		if isinstance(action,list):
			self._dq.extend(action)
		else:
			self._dq.append(action)
		return self

	def put_first(self,action):
		if isinstance(action,list):
			self._dq.extendleft(reversed(action))
		else:
			self._dq.appendleft(action)
		return self

	def do(self):
		global CURRENT_ACTION_RECORD
		CURRENT_ACTION_RECORD = deque()

		tokens = []
		while self._dq:
			x = self._dq.popleft()
			if isinstance(x,CollectReferences):
				x.execute(self.match,self.cache)
			if isinstance(x,PrimaryAction):
				CURRENT_ACTION_RECORD.append(x)
				if isinstance(x,RemoveNode):
					tokens.extend(convert_action_to_tokens(x,self.cache))
					x.execute(self.cache)
				else:	
					x.execute(self.cache)
					tokens.extend(convert_action_to_tokens(x,self.cache))
				self.record.append(x)
			elif isinstance(x,CompositeAction):
				self.put_first(x.expand())
		return tokens



class SimulationEngine:

	ReteNetClass = build_rete_net_class()
	
	def __init__(self,model=None,parameters=None):
		print('Importing model and parameters.')
		model = AggregateModel('model',models=[model])
		model.verify(parameters)
		self.variables = LoggableDict(NestedDict.flatten(parameters))

		self.rules = dict(model.iter_rules())
		self.observables = dict(model.iter_observables())
		self.cache = DictLike()
		self.compiled_rules = dict()

		print('Initializing rete net matching engine.')
		self.net = self.ReteNetClass() \
			.initialize_start() \
			.initialize_end()	\
			.initialize_rules(self.rules,self.variables) \
			.initialize_observables(self.observables)

		self.net.validate()
		print('Linking rules to matching engine.')
		for name,rule in self.rules.items():
			self.compile_rule(name,rule)

		for node in self.net.get_nodes(type='variable'):
			self.variables.set(node.core,node.state.cache.value)

	def get_updated_variables(self):
		# this needs to be removed as it is not used in the simulator
		# it is currently being used by many tests though
		modified = list(self.variables.modified)
		self.variables.flush()
		return modified

	def compile_rule(self,rule_name,rule):
		compilation = AttrDict()
		compilation.original_object = rule
		compilation.reactants = {k:self.net.get_node(core=v).state.cache for k,v in rule.reactants.items()}
		compilation.helpers = {k:self.net.get_node(core=v).state.cache for k,v in rule.helpers.items()}
		compilation.parameters = PrefixSubdict(get_model_name(rule_name),self.variables)
		compilation.action_manager = rule.get_action_manager()
		compilation.factories = rule.factories
		self.compiled_rules[rule_name] = compilation
		return self

	def update(self,variables):
		for variable in variables:
			value = self.net.get_node(core=variable).state.cache.value
			self.variables.set(variable,value)
		return self

	def load(self,obj):
		if isinstance(obj,Sequence):
			for x in obj:
				self.load(x)
			return self
		ax = ActionStack(self.cache,{})
		for action in obj.generate_actions():
			tokens = ax.put(action).do()
			self.net.process_tokens(tokens)
		variables = self.net.get_updated_variables()
		self.update(variables)
		return self

	def fire(self,rule_name):
		rule = self.compiled_rules[rule_name]
		match = AttrDict()
		for name,pcache in rule.reactants.items():
			match[name] = AttrDict(pcache.sample())
		ax = ActionStack(self.cache,match)
		for action in rule.action_manager.exec(ax.match,rule.parameters,rule.reactants,rule.helpers,rule.factories):
			tokens = ax.put(action).do()
			self.net.process_tokens(tokens)
		variables = self.net.get_updated_variables()
		self.update(variables)
		return self
		
	def simulate(self,start=0.0,end=1.0,period=1,write_location=None):
		global CURRENT_ACTION_RECORD
		print(f'Simulating from time={start} to time={end}.')
		time = start
		sch = CoordinatedScheduler([
			NextReactionMethod(),
			PeriodicWriteObservables(
				start=start,
				period=period,
				write_location=write_location
			)])
		sch.update(start,self.variables)
		while True:
			event,time = sch.pop()
			if event=='write_observables':
				print(f'Current time={time}\tNumber of objects={len(self.cache)}')
				self.write_observables(time,write_location)
				if time >= end:
					break
			elif event in self.rules:
				try:
					self.fire(event)
				except Exception as error:
					print(f'While firing {event}, an error occurred.')
					print(f'The following actions were being implemented: ')
					for act in CURRENT_ACTION_RECORD:
						print(act)
					print(f'Simulation failed. Exiting.' )
					raise error.with_traceback(sys.exc_info()[2])
					
				sch.update(time,subdict(self.variables,self.variables.modified))
			self.variables.flush()
		print(f'Simulation complete. Exiting.')
		return self

	def write_observables(self,time,write_location):
		variables = [x.core for x in self.net.get_nodes(type='variable') if x.data.subtype=='recompute']
		write_location.append({'time':time,'observables':subdict(self.variables,variables)})
		return self

