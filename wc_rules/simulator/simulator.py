from collections import deque 

class SimulationState:
	def __init__(self,nodes=[]):
		self.state = {x.id:x for x in nodes}
		# for both stacks, use LIFO semantics using appendleft and popleft
		self.action_stack = deque()
		self.rollback_stack = deque()

	def resolve(self,idx):
		return self.state[idx]

	def update(self,node):
		self.state[node.id] = node
		return self

	def remove(self,node):
		del self.state[node.id]
		del node
		return self

	def get_contents(self,ignore_id=True,ignore_None=True,use_id_for_related=True,sort_for_printing=True):
		d = {x.id:x.get_attrdict(ignore_id=ignore_id,ignore_None=ignore_None,use_id_for_related=use_id_for_related) for k,x in self.state.items()}
		if sort_for_printing:
			# sort list attributes
			for idx,adict in d.items():
				for k,v in adict.items():
					if isinstance(v,list):
						adict[k] = list(sorted(v))
				adict = dict(sorted(adict.items()))
			d = dict(sorted(d.items())) 
		return d

	def push_to_stack(self,action):
		if isinstance(action,list):
			# assume list has to be executed left to right
			self.action_stack = deque(action) + self.action_stack
		else:
			self.action_stack.appendleft(action)
		return self

	def simulate(self):
		while self.action_stack:
			action = self.action_stack.popleft()
			if hasattr(action,'expand'):
				self.push_to_stack(action.expand())
			else:
				self.rollback_stack.appendleft(action.rollback(self))
				action.execute(self)
		return self

	def rollback(self):
		while self.rollback_stack:
			action = self.rollback_stack.popleft()
			action.execute(self)
		return self




