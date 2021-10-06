
from .configuration import ReteNetConfiguration
from .dbase import initialize_database, Record, SEP
from .actions import *
from attrdict import AttrDict
from collections import deque
import logging
import os

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
		d['cache'] = [x for x in self.cache] if self.cache is not None else None
		return Record.print(d,nsep=2)

	def contains(self,**elem):
		return len(self.filter(**elem)) > 0

	def filter(self,**elem):
		return Record.retrieve(self.cache,elem)

	def insert(self,**elem):
		Record.insert(self.cache,elem)
		return self


class ReteNet:

	@classmethod
	def default_initialization(cls):
		return ReteNetConfiguration().configure(cls()).initialize_start()

	def __init__(self):
		self.nodes = initialize_database(['type','core','data','state','num'])
		self.channels = initialize_database(['type','source','target','data','num'])
		self.nodemax = 0
		self.channelmax = 0

	def add_node(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','core']}
		record.update(dict(data=kwargs,state=ReteNodeState()))
		record['num'] = self.nodemax
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

	def pprint(self,state=False):
		s = []

		def printfn(x):
			return Record.print(node,ignore_keys=['state','num'])

		for node in self.nodes:
			s += [f"Node {node.get('num')}\n{printfn(node)}"]
			if state:
				s1 = node['state'].pprint()
				if s1:
					s[-1] += f'\n{SEP}state:\n{s1}'

		for channel in self.channels:
			s += [f"Channel {channel.get('num')}\n{Record.print(channel,ignore_keys=['num'])}"]
		return '\n'.join(s)

	def sync(self,node):
		log.debug(f'Syncing node {node.core}')
		if node.state.outgoing:
			log.debug(f'{SEP}Outgoing: {node.state.outgoing}')
			elem = node.state.outgoing.popleft()
			channels = self.get_outgoing_channels(node.core)
			for channel in channels:
				log.debug(f'{SEP}Channel: {channel}')
				method = getattr(self,f'function_channel_{channel.type}')
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
		return

