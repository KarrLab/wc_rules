from ..schema.base import BaseClass
from ..utils.collections import UniversalSet
from .token import TokenTransformer
from ..graph.graph_partitioning import partition_canonical_form

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
		elif len(clabel.names)==2:
			self.initialize_canonical_label_single_edge(clabel,symmetry_group)
		else:
			self.initialize_canonical_label_general_case(clabel,symmetry_group)
		return self

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

	def initialize_canonical_label_general_case(self,clabel,symmetry_group):
		# dummy code, need to reimplement and test
		(m1,L1,G1), (m2,L2,G2) = partition_canonical_form(clabel,symmetry_group)
		self.initialize_canonical_label(L1,G1)
		self.initialize_canonical_label(L2,G2)
		actionmap = {'AddEntry':'AddPartialEntry', 'RemoveEntry':'RemovePartialEntry'}
		self.add_node_canonical_label(clabel,symmetry_group)
		channel_nums = [self.channelmax, self.channelmax+1]
		self.add_channel_transform(source=L1,target=clabel,datamap=m1._dict,actionmap=actionmap)
		self.add_channel_transform(source=L2,target=clabel,datamap=m2._dict,actionmap=actionmap)
		caches = {
			'lhs': self.generate_cache_reference(L1,m1.reverse()._dict),
			'rhs': self.generate_cache_reference(L2,m2.reverse()._dict)
		}
		channels = dict(zip(channel_nums,['lhs','rhs']))
		self.update_node_data(clabel,dict(caches=caches,channels=channels))

		return self



