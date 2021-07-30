from pydblite import Base as dBase
from frozendict import frozendict
from ..utils.collections import subdict
from types import MethodType
from . import rete_node
from ..schema.entity import Entity

# Here, core refers to the "core element" of a rete-node.
# This may be an edge, a graph ,a pattern, a rule, etc.

class ReteNet:

	methods = rete_node.initializers

	def __init__(self):
		self.nodes = dict()
		self.channels = dBase(':memory:')
		self.channels.create('source','target','chtype','misc')
		self.configure()

	def configure(self):
		for method in self.__class__.methods:
			self.bind_method(method)
		return self

	def add_node(self,node):
		assert isinstance(node,rete_node.ReteNode)
		if node.core not in self.nodes:
			self.nodes[node.core] = node

		# register node
		return self

	def add_channel(self,source,target,chtype,**kwargs):
		assert isinstance(source,rete_node.ReteNode)
		assert isinstance(target,rete_node.ReteNode)
		kwargs = frozendict(kwargs) if kwargs else None
		channel = dict(source=source,target=target,chtype=chtype,misc=kwargs)
		if not self.channels(**channel):
			self.channels.insert(**channel)

		# register channel
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
		for x in self.nodes:
			s.append('Node '+str(x))
		for channel in self.channels:
			s.append(f"Channel {str(channel['source'].core)} -> {str(channel['target'].core)}, {channel['chtype']}, {channel['misc']}")
		return '\n'.join(s)





