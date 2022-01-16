from attrdict import AttrDict
from collections import deque
import random
import logging
import os
from types import MethodType

from .dbase import initialize_database, Record, SEP
from .initialize import default_initialization_methods
from .functionalize import default_functionalization_methods


log = logging.getLogger(__name__)
FORMAT = '%(message)s'
logging.basicConfig(level=os.environ.get("LOGLEVEL","NOTSET"), format=FORMAT)

log.propagate = False

# testing new rete-net functionality
# first test initialization
# then test propagation using ReteNet.sync()
# then test function_{}_{}

class ReteNodeState:

	def __init__(self):
		self.cache = None
		self.incoming = deque()
		self.outgoing = deque()
		
	def pprint(self,nsep=2):
		d = dict(incoming=self.incoming,outgoing=self.outgoing)
		try:
			d['cache'] = [x for x in self.cache] if self.cache is not None else None
		except:
			d['cache'] =self.cache
		return Record.print(d,nsep=2)

	def contains(self,**elem):
		return len(self.filter(**elem)) > 0

	def filter(self,**elem):
		return Record.retrieve(self.cache,elem)

	def insert(self,**elem):
		Record.insert(self.cache,elem)
		return self

	def count(self,**elem):
		#print(len(self.filter(**elem)))
		return len(self.filter(**elem))

	def sample_cache(self):
		return dict(Record.itemize(random.choice(self.filter())))
		
class ReteNodeStateWrapper:
	# wrapper is useful to manage aliases
	# typically a node's wrapper maps to the node's state with 
	# an identity mapping
	# if an alias, then the wrapper points to the parent's state
	# and the mapping is used to convert in both directions

	def __init__(self,target,mapping=None):
		self.target = target
		self.mapping = mapping

	def __getattr__(self,name):
		def fn():
			return getattr(self.target,name)()
		return fn

	def set(self,target,mapping=None):
		self.target = target
		self.mapping = mapping
		return self
		
class ReteNet:

	# tracer is used for capturing output of specific nodes

	def __init__(self):
		self.nodes = initialize_database(['type','core','data','state','wrapper','num'])
		self.channels = initialize_database(['type','source','target','data','num'])
		self.tracer = False
		self.nodemax = 0
		self.channelmax = 0

	def configure(self,method,overwrite=False):
		m = MethodType(method, self)
		assert overwrite or method.__name__ not in dir(self)
		setattr(self,method.__name__,m)
		return self

	def configure_tracer(self,nodes=[],channels=[]):
		self.tracer = AttrDict(nodes=nodes,channels=channels)
		return self

	def add_node(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','core']}
		record.update(dict(data=kwargs,state=ReteNodeState()))
		record['num'] = self.nodemax
		record['wrapper'] = ReteNodeStateWrapper(record['state'])
		Record.insert(self.nodes,record)
		self.nodemax += 1
		return self

	def get_node(self,**kwargs):
		node = Record.retrieve_exactly(self.nodes,kwargs)
		return AttrDict(node) if node else None

	def initialize_cache(self,core,variables=None):
		node = self.get_node(core=core)
		if variables is not None:
			node.state.cache = initialize_database(variables)
		else:
			node.state.cache = deque()
		return self

	def filter_cache(self,core,elem):
		node = self.get_node(core=core)
		if node.data.get('alias',False):
			ch = self.get_channel(target=core,type='alias')
			elem = ch.data.mapping.reverse().transform(elem)
			return self.filter_cache(core=ch.source,elem=elem)		
		return Record.retrieve(node.state.cache,elem)

	def insert_into_cache(self,core,elem):
		node = self.get_node(core=core)
		Record.insert(node.state.cache,elem)
		return self

	def remove_from_cache(self,core,elem):
		node = self.get_node(core=core)
		Record.remove(node.state.cache,elem)
		return self

	def add_channel(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','source','target']}
		record.update(dict(data=kwargs))
		record['num'] = self.channelmax +1
		Record.insert(self.channels,record)
		self.channelmax += 1
		return self

	def get_channel(self,**kwargs):
		channel = Record.retrieve_exactly(self.channels,kwargs) 
		return AttrDict(channel) if channel else None

	def get_outgoing_channels(self,source):
		return [AttrDict(ch) for ch in Record.retrieve(self.channels,{'source':source})]

	def get_channels(self,include_kwargs,exclude_kwargs=None):
		includes = Record.retrieve_minus(self.channels,include_kwargs,exclude_kwargs) if exclude_kwargs is not None else Record.retrieve(self.channels,include_kwargs)
		return [AttrDict(ch) for ch in includes]

	def pprint_node(self,num,state=False):
		s = []
		node = self.get_node(num=num)
		desc = Record.print(node,ignore_keys=['state','num'])
		s += [f"Node {num}\n{desc}"]
		if state:
			s1 = node['state'].pprint()
			s[-1] += f'\n{SEP}state:\n{s1}'
		return '\n'.join(s)

	def trace_node(self,num):
		return self.tracer and num in self.tracer.nodes
	
	def trace_channel(self,num):
		return self.tracer and num in self.tracer.channels
			
	def trace_elem(self,elem):
		if self.tracer:
			print

	def pprint_channel(self,num):
		channel = self.get_channel(num=num)
		desc = Record.print(channel,ignore_keys=['num'])
		return f"Channel {num}\n{desc}"

	def pprint(self,state=False):
		s = []
		for node in self.nodes:
			s.append(self.pprint_node(node.get('num'),state=state))
		for channel in self.channels:
			s.append(self.pprint_channel(channel.get('num')))
		return '\n'.join(s)

	def sync(self,node):
		num = node.get('num')
		trace = self.trace_node(num)
		if node.state.outgoing:
			if trace:
				print(self.pprint_node(num,state=True))
			log.debug(f'{SEP}Outgoing: {node.state.outgoing}')
			elem = node.state.outgoing.popleft()
			if trace:
				print(f'Popping elem {elem}')
			channels = self.get_outgoing_channels(node.core)
			for channel in channels:
				chnum = channel.get('num')
				log.debug(f'{SEP}Channel: {channel}')
				method = getattr(self,f'function_channel_{channel.type}')
				if self.trace_channel(chnum):
					print(self.pprint_channel(chnum))
				method(channel,elem)
				self.sync(self.get_node(core=channel.target))
			self.sync(node)
		if node.state.incoming:
			log.debug(f'{SEP}Incoming: {node.state.incoming}')
			elem = node.state.incoming.popleft()
			method = getattr(self,f'function_node_{node.type}')
			method(node,elem)
			self.sync(node)

		return self

	def process(self,tokens):
		start = self.get_node(type='start')
		for token in tokens:
			start.state.incoming.append(token)
			self.sync(start)

		endnode = self.get_node(core='end')
		outtokens = []
		while endnode.state.cache:
			outtokens.append(endnode.state.cache.popleft())
			
		return outtokens

def default_rete_net(start=True,end=True):
	net = default_configuration().configure(ReteNet())
	if start:
		net.initialize_start()
	if end:
		net.initialize_end()
	return net

default_rete_net_methods =  default_initialization_methods + default_functionalization_methods
