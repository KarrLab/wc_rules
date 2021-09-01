from collections import deque
from frozendict import frozendict
from types import MethodType

from ..schema.base import BaseClass
from attrdict import AttrDict
from pydblite import Base as dBase

class SimulationObject(AttrDict):
	pass

class ReteNode:

	def __init__(self,core,**data):
		# label is a hashable label produced from any core object in the model
		self.core = core
		self.data = frozendict(data) if data else None
		self.slots = deque()
		self.cache = None

class ReteNet:

	def __init__(self,methods=[]):
		self.nodes = dict()
		self.channels = dBase(':memory:')
		self.channels.create('source','target','chtype','data')
		self.configure(methods)

	def configure(self,methods):
		for method in methods:
			self.bind_method(method)
		return self

	def resolve_node(self,label):
		return self.nodes[label]

	def add_node(self,label,core,**data):
		assert label not in self.nodes
		self.nodes[label] = ReteNode(core,**data)
		return self

	def add_channel(self,source,target,chtype,**data):
		assert all([x in self.nodes for x in [source,target]])
		data = frozendict(data) if data else None
		channel = dict(source=source,target=target,chtype=chtype,data=data)

		if not self.filter_channels(**channel):
			self.channels.insert(**channel)
		return self

	def bind_method(self,method):
		m = MethodType(method, self)
		assert method.__name__ not in dir(self)
		setattr(self,method.__name__,m)
		return self

	def list_methods(self):
		return [x for x in dir(self) if x[0:2]!='__' and isinstance(getattr(self,x),MethodType)]

	def pprint(self):
		s = []
		for label,node in self.nodes.items():
			s.append(f"Node {label}: {id(node)}: {node.core}")
		for channel in self.channels:
			s.append(f"Channel {channel['chtype']} {str(channel['source'])} -> {str(channel['target'])},  {channel['data']}")
		return '\n'.join(s)

	def filter_channels(self,**kwargs):
		return self.channels(**kwargs)


