from ..utils.collections import UniversalSet, SimpleMapping
from ..schema.base import BaseClass
from .dbase import Database, DatabaseAlias, DatabaseSingleValue, DatabaseSymmetric, DatabaseAliasSymmetric
from .token import TokenTransformer

from collections import deque

class AddMethods:

	DATABASE_CLASS = Database
	DATABASE_SINGLE_VALUE  = DatabaseSingleValue
	DATABASE_ALIAS_CLASS = DatabaseAlias

	def add_node_start(self):
		self.add_node(type='start',core=BaseClass)
		return self

	def add_node_end(self):
		self.add_node(type='end',core='end',cache=deque())
		return self

	def add_node_class(self,_class):
		self.add_node(type='class',core=_class)
		return self

	def add_node_receiver(self,core_object,receiver_name):
		self.add_node(type='receiver',core=receiver_name,cache=deque())
		return self

	def add_node_alias(self,type,core_object,reference_object,mapping):
		cache_ref = self.generate_cache_reference(core=reference_object,mapping=mapping)
		self.add_node(type='pattern',core=core_object,)

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

	def add_node_pattern(self,pattern,cache,subtype='default',executables=[],caches={}):
		self.add_node(
			type = 'pattern',
			core = pattern,
			cache = cache,
			subtype = subtype,
			executables=executables,
			caches = caches
			)

	def add_node_variable(self,name,default_value=None,executable=None,parameters={},caches={},subtype=None):
		self.add_node(
			type='variable',
			core=name,
			cache=self.DATABASE_SINGLE_VALUE(value=default_value),
			executable = executable,
			parameters = parameters,
			caches=caches,
			subtype=subtype
			)

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

	def generate_cache(self,fields,**kwargs):	
		return self.DATABASE_CLASS(fields=fields,**kwargs)

	def update_node_data(self,core,update_dict):
		data = self.get_node(core=core).data
		data.update(update_dict)
		self.nodes.update({'core':core},{'data':data})

	def add_channel_pass(self,source,target,allowed_token_actions=UniversalSet(),filter_data=lambda data: True):
		self.add_channel(
			type='pass',
			source=source,
			target=target,
			allowed_token_actions=allowed_token_actions,
			filter_data = filter_data
		)
		return self

	def add_channel_transform(self,source,target,datamap,actionmap,filter_data=lambda data: True):
		self.add_channel(
			type='transform',
			source=source,
			target=target,
			allowed_token_actions=actionmap.keys(),
			transformer = TokenTransformer(datamap,actionmap),
			filter_data = filter_data
		)		
		return self

	def add_channel_variable_update(self,source,target,variable):
		self.add_channel(
			type = 'variable_update',
			source = source,
			target = target,
			variable = variable
			)
		return self


class AddMethodsSymmetric(AddMethods):

	DATABASE_CLASS = DatabaseSymmetric
	DATABASE_ALIAS_CLASS = DatabaseAliasSymmetric
