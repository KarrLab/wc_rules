from ..utils.collections import UniversalSet
from ..schema.base import BaseClass
from .token import TokenTransformer

class AddMethods:

	def add_node_start(self):
		self.add_node(type='start',core=BaseClass)
		return self

	def add_node_class(self,_class):
		self.add_node(type='class',core=_class)
		return self

	def add_node_receiver(self,core_object,receiver_name):
		self.add_node(type='receiver',core=receiver_name,cachetype='deque')
		return self

	def add_node_canonical_label(self,clabel,symmetry_group):
		self.add_node(
			type = 'canonical_label',
			core = clabel,
			symmetry_group=symmetry_group,
			cachetype='database',
			fields = clabel.names
			)
		return self

	def add_channel_pass(self,source,target,allowed_token_actions=UniversalSet()):
		self.add_channel(
			type='pass',
			source=source,
			target=target,
			allowed_token_actions=allowed_token_actions
		)
		return self

	def add_channel_transform(self,source,target,datamap,actionmap):
		self.add_channel(
			type='transform',
			source=source,
			target=target,
			allowed_token_actions=actionmap.keys(),
			transformer = TokenTransformer(datamap,actionmap)
		)		
		return self
