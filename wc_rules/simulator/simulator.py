from collections import deque 
from ..matcher.core import ReteNet
from ..matcher.actions import make_node_token, make_edge_token, make_attr_token

class SimulationState:
	def __init__(self,nodes=[],**kwargs):
		self.state = {x.id:x for x in nodes}
		# for both stacks, use LIFO semantics using appendleft and popleft
		self.action_stack = deque()
		self.rollback_stack = deque()
		self.matcher = kwargs.get('matcher',ReteNet.default_initialization())

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
			elif action.__class__.__name__ == 'RemoveNode':
				self.rollback_stack.appendleft(action)
				matcher_tokens = self.compile_to_matcher_tokens(action)
				action.execute(self)
				self.matcher.process(matcher_tokens)
			else:
				self.rollback_stack.appendleft(action)
				action.execute(self)
				matcher_tokens = self.compile_to_matcher_tokens(action)
				self.matcher.process(matcher_tokens)
		return self

	def rollback(self):
		while self.rollback_stack:
			action = self.rollback_stack.popleft()
			action.execute(self)
		return self

	def compile_to_matcher_tokens(self,action):
		action_name = action.__class__.__name__
		#d = {'AddNode':'add','RemoveNode':'remove','AddEdge':'add','RemoveEdge':'remove'}
		# NOTE: WE"RE ATTACHING ACTUAL NODES HERE, NOT IDS, FIX action.idx,idx1,idx2 later
		if action_name in ['AddNode','RemoveNode']:
			return [make_node_token(action._class, self.resolve(action.idx), action_name)]
		if action_name in ['SetAttr']:
			_class = self.resolve(action.idx).__class__
			return [make_attr_token(_class, self.resolve(action.idx), action.attr, action.value, action_name)]
		if action_name in ['AddEdge','RemoveEdge']:
			i1,a1,i2,a2 = [getattr(action,x) for x in ['source_idx','source_attr','target_idx','target_attr']]
			c1,c2 = [self.resolve(x).__class__ for x in [i1,i2]]
			return [
				make_edge_token(c1,self.resolve(i1),a1,self.resolve(i2),a2,action_name),
				make_edge_token(c2,self.resolve(i2),a2,self.resolve(i1),a1,action_name)
			]
		return []
				





