from ..utils.collections import DictLike
from collections import deque

class SimulationState(DictLike):
	pass

class VariableDictionary:

	def __init__(self):
		self._dict = dict()
		self.updated = set()
		self.vartypes = dict()

	def update(self,variable,vartype,value=None):
		# do not use None as a legal value
		# it is to be used only for manually updating self.updated
		if variable not in self._dict:
			self.vartypes[variable] = vartype
		if value is not None:
			self._dict[variable] = value
		self.updated.add(variable)
		return self

	def retrieve(self,variable,vartype):
		return self._dict[variable]

	def flush(self):
		self.updated = set()
		return self

class Timer:

	def __init__(self,start=0.0,end=float('inf'),current=None):
		self.start = start
		self.end = end
		self.current=start if current is None else current
		self.previous = start

	def next_event_possible(self):
		return self.current <= self.end

	def update(self,time):
		self.previous, self.current = self.current, time
		return self

class ActionQueue:

	def __init__(self,actions):
		self.actions = deque(actions)
		self.record = deque()
		
	def push(self,action):
		if isinstance(action,list):
			# assume list has to be executed left to right
			self.actions = deque(action) + self.actions
		else:
			self.actions.appendleft(action)
		return self

	def pop(self):
		return self.actions.popleft()

	def execute(self,simulation_state):
		tokens = []
		while self.actions:
			action = self.pop()
			if hasattr(action,'expand'):
				self.push(action.expand())
			else:
				tokens += action.execute(simulation_state)
				self.record.append(action)
		return tokens



