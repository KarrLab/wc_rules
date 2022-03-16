from ..utils.collections import UniversalSet, SimpleMapping
from ..schema.base import BaseClass
from .dbase import Database, DatabaseAlias, DatabaseSymmetric, DatabaseAliasSymmetric
from .token import TokenTransformer

from collections import deque

class AddMethods:

	DATABASE_CLASS = Database
	DATABASE_ALIAS_CLASS = DatabaseAlias

	def add_node_start(self):
		self.add_node(type='start',core=BaseClass)
		return self

	def add_node_class(self,_class):
		self.add_node(type='class',core=_class)
		return self

	def add_node_receiver(self,core_object,receiver_name):
		self.add_node(type='receiver',core=receiver_name,cache=deque())
		return self

	def add_node_canonical_label(self,clabel,symmetry_group):
		cache = self.DATABASE_CLASS(
			fields=clabel.names,
			symmetry_group=symmetry_group
		)
		self.add_node(
			type = 'canonical_label',
			core = clabel,
			cache = cache
			)
		return self

	def add_data_property(self,core,variable,value):
		node = self.get_node(core=core)
		node.data[variable]=value
		return self

	def generate_cache_reference(self,target,mapping,symmetry_group=None):
		target_node = self.get_node(core=target)
		cache_ref = self.DATABASE_ALIAS_CLASS(
			target=target_node.state.cache,
			mapping=SimpleMapping(mapping),
			symmetry_group=symmetry_group,
		)
		return cache_ref

	def update_node_data(self,core,update_dict):
		data = self.get_node(core=core).data
		data.update(update_dict)
		self.nodes.update({'core':core},{'data':data})

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

class AddMethodsSymmetric(AddMethods):

	DATABASE_CLASS = DatabaseSymmetric
	DATABASE_ALIAS_CLASS = DatabaseAliasSymmetric
