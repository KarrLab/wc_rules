from collections import deque 
from ..utils.collections import DictLike, subdict
from ..matcher.core import default_rete_net
from ..matcher.actions import make_node_token, make_edge_token, make_attr_token
from .sampler import default_sampler
from attrdict import AttrDict

def make_timekeeper(d):
	t = AttrDict({'start':0.0,'end':None,'current':0.0,'record_interval':None,'next_record_time':None})
	if 'start_time' in d:
		t.start = d['start_time']
		t.current = d['start_time']
	if 'end_time' in d:
		t.end = d['end_time']
	if 'current_time' in d:
		t.current = d['current_time']
	if 'record_interval' in d:
		t.record_interval = d['record_interval']
	return t

class Simulator:
	def __init__(self,model=None,simstate=[],config=dict()):
		self.cache = DictLike()
		self.model = model

		self.matcher = config.get('matcher',default_rete_net())
		self.sampler = config.get('sampler',default_sampler())		
		
		self.timekeeper = make_timekeeper(config)
		
		self.action_stack = deque()
		self.rollback_stack = deque()

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

	def load_nodes_into_matcher(self,nodes):
		for x in nodes:
			self.matcher.process([make_node_token(x.__class__,x,'AddNode')])
			for a,y in x.iter_edges():
				a1 = x.get_related_name(a)
				self.matcher.process([make_edge_token(x.__class__,x,a,y,a1,'AddEdge')])
		return self

	def load_state(self,nodes):
		for x in nodes:
			self.cache.add(x)
		if self.matcher is not None:
			self.load_nodes_into_matcher(self,nodes)
		return self

	def load_matcher(self,matcher):
		# ALWAYS ADD STATE TO A PRECONFIGURED MATCHER/SAMPLER
		# NEVER THE OTHER WAY AROUND
		assert len(self.cache) == 0
		self.matcher = matcher
		return self





class SimulationState:
	def __init__(self,nodes=[],**kwargs):
		self.cache = DictLike(nodes)
		# for both stacks, use LIFO semantics using appendleft and popleft
		self.rollback = kwargs.get('rollback',False)
		self.action_stack = deque()
		self.rollback_stack = deque()
		self.matcher = kwargs.get('matcher',default_rete_net())
		
		self.start_time = kwargs.get('start_time',0.0)
		self.end_time = kwargs.get('end_time',0.0)
		self.sampler = kwargs.get('sampler',default_sampler(time=kwargs.get('start_time',0.0)))

	# These are elementary methods, used as 
	# the final step in adding/removing a node
	def resolve(self,idx):
		return self.cache.get(idx)

	def update(self,node):
		self.cache.add(node)
		return self

	def remove(self,node):
		self.cache.remove(node)
		return self

	def get_contents(self,ignore_id=True,ignore_None=True,use_id_for_related=True,sort_for_printing=True):
		d = {x.id:x.get_attrdict(ignore_id=ignore_id,ignore_None=ignore_None,use_id_for_related=use_id_for_related) for k,x in self.cache.items()}
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
				if self.rollback:
					self.rollback_stack.appendleft(action)
				matcher_tokens = self.compile_to_matcher_tokens(action)
				action.execute(self)
				outtokens = self.matcher.process(matcher_tokens)
			else:
				if self.rollback:
					self.rollback_stack.appendleft(action)
				action.execute(self)
				matcher_tokens = self.compile_to_matcher_tokens(action)
				outtokens = self.matcher.process(matcher_tokens)

		self.update_sampler(outtokens)
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

	def update_sampler(self,tokens):
		for token in tokens:
			self.sampler.update_propensity(reaction=token['source'],propensity=token['propensity'])
		return self

	def sample_next_event(self):
		rule,time = self.sampler.next_event()
		if time == float('inf'):
			print('Null event!')
			return self
		sample = self.matcher.function_sample_rule(rule)
		rule_node = self.matcher.get_node(core=rule,type='rule')
		for act in rule_node.data.actions:
			if act.deps.declared_variable is not None:
				sample[act.deps.declared_variable] = act.exec(sample,rule_node.data.helpers)
			else:
				self.push_to_stack(act.exec(sample,rule_node.data.helpers))
		self.sampler.update_time(time)
		self.simulate()
		return self			




