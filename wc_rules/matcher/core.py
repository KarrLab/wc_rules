from types import MethodType
from attrdict import AttrDict

from .dbase import Database
from .add_methods import AddMethods, AddMethodsSymmetric
from .initialize_methods import InitializationMethods
from .state import ReteNodeState
from .node_functions import NodeFunctions
from .channel_functions import ChannelFunctions
from ..utils.collections import UniversalSet

bases = [AddMethods, InitializationMethods, NodeFunctions, ChannelFunctions]

class ReteNetBase:

	def __init__(self):
		self.nodes = Database(['type','core','data','state','num'])
		self.channels = Database(['type','source','target','data','num'])
		self.nodemax = 0
		self.channelmax = 0

	def get_node(self,**kwargs):
		node = self.nodes.filter_one(kwargs)
		return AttrDict(node) if node is not None else None

	def get_nodes(self,**kwargs):
		return [AttrDict(x) for x in self.nodes.filter(kwargs)]

	def get_channel(self,**kwargs):
		channel = self.channels.filter_one(kwargs)
		return AttrDict(channel) if channel is not None else None

	def get_channels(self,**kwargs):
		return [AttrDict(x) for x in self.channels.filter(kwargs)]
		
	def add_node(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','core']}
		record['state'] = ReteNodeState(cache=kwargs.pop('cache',None))
		record['data'] = kwargs
		record['num'] = self.nodemax
		self.nodes.insert(record)
		self.nodemax +=1
		return self

	def add_channel(self,**kwargs):
		record = {k:kwargs.pop(k) for k in ['type','source','target']}
		record['data'] =kwargs
		record['num'] = self.channelmax
		self.channels.insert(record)
		self.channelmax += 1
		return self

	def sync_outgoing(self,node):
		token = node.state.outgoing.popleft()
		channels = self.get_channels(source=node.core)
		for channel in channels:
			if token.action in channel.data.allowed_token_actions:
				method = getattr(self,f'function_channel_{channel.type}')
				method(channel,token)
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


def build_rete_net_class(bases=bases,name='ReteNet',symmetry_aware=False):
	all_bases = [ReteNetBase,] + bases
	if symmetry_aware:
		all_bases[all_bases.index(AddMethods)]= AddMethodsSymmetric
	ReteNet = type(name,tuple(all_bases),{})
	return ReteNet