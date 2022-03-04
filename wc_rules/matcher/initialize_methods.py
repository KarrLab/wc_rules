from ..schema.base import BaseClass
from ..utils.collections import UniversalSet
from .token import TokenTransformer

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
		self.add_node_start()
		return self

	def initialize_class(self,_class):
		if self.node_exists(core=_class):
			return self

		parent = _class.__mro__[1]
		self.initialize_class(parent)
		self.add_node_class(_class)
		self.add_channel_pass(source=parent,target=_class)
		return self

	def initialize_receiver(self,**kwargs):
		node = self.get_node(**kwargs)
		receiver_name = f'receiver_{node.num}'
		
		if self.node_exists(core=receiver_name):
			return self

		self.add_node_receiver(node.core,receiver_name)
		self.add_channel_pass(node.core,receiver_name)
		return self

	def initialize_canonical_label(self,clabel,symmetry_group):
		if self.node_exists(core=clabel):
			return self

		if len(clabel.names)==1:
			self.initialize_canonical_label_single_node(clabel,symmetry_group)

		if len(clabel.names)==2:
			self.initialize_canonical_label_single_edge(clabel,symmetry_group)

	def initialize_canonical_label_single_node(self,clabel,symmetry_group):
		self.initialize_class(clabel.classes[0])
		self.add_node_canonical_label(clabel,symmetry_group)
		datamap = {'ref':'a'}
		actionmap = {'AddNode':'AddEntry','RemoveNode':'RemoveEntry'}
		self.add_channel_transform(clabel.classes[0],clabel,datamap,actionmap)
		return self

	def initialize_canonical_label_single_edge(self,clabel,symmetry_group):
		self.initialize_class(clabel.classes[0])
		self.add_node_canonical_label(clabel,symmetry_group)
		datamap = {'ref1':'a','ref2':'b','attr1':'attr1','attr2':'attr2'}
		actionmap = {'AddEdge':'AddEntry','RemoveEdge':'RemoveEntry'}
		self.add_channel_transform(clabel.classes[0],clabel,datamap,actionmap)
		return self





