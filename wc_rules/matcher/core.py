
from collections import deque
from .configuration import ReteNetConfiguration
from .dbase import initialize_database, Record
from attrdict import AttrDict

class ReteNodeState:

	def __init__(self):
		self.cache = None
		self.incoming = deque()
		self.outgoing = deque()


class ReteNet:

	@classmethod
	def default_initialization(cls):
		return ReteNetConfiguration().configure(cls()).initialize_start()

	def __init__(self):
		self.nodes = initialize_database(['type','core','data','state'])
		self.channels = initialize_database(['type','source','target','data'])

	def add_node(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','core']}
		record.update(dict(data=kwargs,state=ReteNodeState()))
		Record.insert(self.nodes,record)
		return self

	def get_node(self,**kwargs):
		node = Record.retrieve_exactly(self.nodes,kwargs)
		return AttrDict(node) if node else None

	def add_channel(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','source','target']}
		record.update(dict(data=kwargs))
		Record.insert(self.channels,record)
		return self

	def get_channel(self,**kwargs):
		channel = Record.retrieve_exactly(self.channels,kwargs) 
		return AttrDict(channel) if channel else None

	def get_outgoing_channels(self,source):
		return [AttrDict(ch) for ch in Record.retrieve(self.channels,{'source':source})]

	def pprint(self):
		s = []
		for node in self.nodes:
			s += [f'Node\n{Record.print(node)}']
		for channel in self.channels:
			s += [f'Channel\n{Record.print(channel)}']
		return '\n'.join(s)

	def sync(self,node):
		if node.state.outgoing:
			elem = node.state.outgoing.popleft()
			channels = self.get_outgoing_channels(node.core)
			for channel in channels:
				method = getattr(self,f'function_channel_{channel.type}')
				method(channel,elem)
				self.sync(self.get_node(core=channel.target))
			self.sync(node)
		if node.state.incoming:
			elem = node.state.incoming.popleft()
			method = getattr(self,f'function_node_{node.type}')
			method(node,elem)
			self.sync(node)
		return self

