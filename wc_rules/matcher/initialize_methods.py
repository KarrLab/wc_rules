from ..schema.base import BaseClass
from ..utils.collections import Mapping, UniversalSet

class InitializationMethods:

	def node_exists(self,**kwargs):
		return self.get_node(**kwargs) is not None

	# FOLLOW THIS TEMPLATE
	# def initialize_x(self,**kwargs):
	# ...compute stuff
	# ...if self.node_exists(x):
	# ...	return self
	# ...if case 1:
	# ...	initialize x
	# ...if case 2:
	# ...	initialize x
	# ...return self

	def initialize_start(self):
		self.add_node(type='start',core=BaseClass)
		return self

	def add_channel_pass(self,source,target):
		self.add_channel(type='pass',source=source,target=target,allowed_token_actions=UniversalSet())		
		return self

	def initialize_class(self,_class):
		if self.node_exists(core=_class):
			return self

		parent = _class.__mro__[1]
		self.initialize_class(parent)
		self.add_node(type='class',core=_class)
		self.add_channel_pass(source=parent,target=_class)
		return self

	def initialize_receiver(self,**kwargs):
		node = self.get_node(**kwargs)
		receiver_name = f'receiver_{node.num}'
		
		if self.node_exists(core=receiver_name):
			return self

		self.add_node(type='receiver',core=receiver_name,cachetype='deque')
		self.add_channel_pass(source=node.core,target=receiver_name)

		return self

	def initialize_canonical_label(self,clabel,symmetry_group):
		if self.node_exists(core=clabel):
			return self

		if len(clabel.names)==1:
			self.initialize_canonical_label_single_node(clabel,symmetry_group)

	def initialize_canonical_label_single_node(self,clabel,symmetry_group):
		self.initialize_class(clabel.classes[0])
		node_args = dict(
			type = 'canonical_label',
			core = clabel,
			symmetry_group=symmetry_group,
			cachetype='database',
			fields = clabel.names
			)
		self.add_node(**node_args)
		channel_args = dict(
			type = 'pass',
			source = clabel.classes[0],
			target = clabel
			)
		self.add_channel(**channel_args)
		
		return self



