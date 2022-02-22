from types import MethodType
from attrdict import AttrDict

from .dbase import Database
from .initialize import InitializeBehaviors
from .state import ReteNodeState
from .functionalize_nodes import FunctionalizeNodes
from .functionalize_channels import FunctionalizeChannels

bases = [InitializeBehaviors, FunctionalizeNodes, FunctionalizeChannels]

class ReteNetBase:

	def __init__(self):
		self.nodes = Database(['type','core','data','state','num'])
		self.channels = Database(['type','source','target','data','num'])
		self.nodemax = 0
		self.channelmax = 0

	def get_node(self,**kwargs):
		node = self.nodes.filter_one(kwargs)
		return AttrDict(node) if node is not None else None

	def get_channel(self,**kwargs):
		channel = self.channels.filter_one(kwargs)
		return AttrDict(channel) if channel is not None else None

	def get_outgoing_channels(self,node):
		channels = self.channels.filter(dict(source=node.core))
		return [AttrDict(x) for x in channels]
	
	def add_node(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','core']}
		record['state'] = ReteNodeState(cachetype = kwargs.pop('cachetype',None))
		record['data'] = kwargs
		record['num'] = self.nodemax
		self.nodes.insert(record)
		self.nodemax +=1
		return self

	def add_channel(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','source','target']}
		record['data'] =kwargs
		record['num'] = self.channelmax +1
		self.channels.insert(record)
		self.channelmax += 1
		return self

	def sync_outgoing(self,node):
		elem = node.state.outgoing.popleft()
		channels = self.get_outgoing_channels(node)
		for channel in channels:
			method = getattr(self,f'function_channel_{channel.type}')
			method(channel,elem)
			self.sync(self.get_node(core=channel.target))
		return self

	def sync_incoming(self,node):
		token = node.state.incoming.popleft()
		method = getattr(self,f'function_node_{node.type}')
		method(node,token)
		return self

	def sync(self,node):
		if node.state.outgoing:
			self.sync_outgoing(node)
			self.sync(node)
		if node.state.incoming:
			self.sync_incoming(node)
			self.sync(node)
		return self




def build_rete_net_class(bases=bases,name='ReteNet'):
	ReteNet = type(name,(ReteNetBase,) + tuple(bases),{})
	return ReteNet