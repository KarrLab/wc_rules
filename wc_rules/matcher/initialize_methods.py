from ..schema.base import BaseClass
from ..modeling.pattern import Pattern, GraphContainer
from ..utils.collections import UniversalSet, triple_split
from .token import TokenTransformer
from ..graph.graph_partitioning import partition_canonical_form
from ..graph.canonical_labeling import canonical_label
from ..graph.permutations import Mapping
from ..expressions.executable import ExecutableExpressionManager
from functools import partial

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

	def initialize_end(self):
		self.add_node_end()
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
		(m1,L1,G1), (m2,L2,G2) = partition_canonical_form(clabel,symmetry_group)
		self.initialize_canonical_label(L1,G1)
		self.initialize_canonical_label(L2,G2)
		
		self.add_node_canonical_label(clabel,symmetry_group)
		
		channel_nums = [self.channelmax, self.channelmax+1]
		channels = dict(zip(channel_nums,['lhs','rhs']))
		actionmap = {'AddEntry':'AddPartialEntry', 'RemoveEntry':'RemovePartialEntry'}
		self.add_channel_transform(source=L1,target=clabel,datamap=m1._dict,actionmap=actionmap)
		self.add_channel_transform(source=L2,target=clabel,datamap=m2._dict,actionmap=actionmap)
		
		lhs_cache = self.generate_cache_reference(L1,m1.reverse()._dict) 
		rhs_cache = self.generate_cache_reference(L2,m2.reverse()._dict)
		caches = {'lhs':lhs_cache,'rhs':rhs_cache}

		keysplit = triple_split(lhs_cache.fields,rhs_cache.fields)
		keysep = dict(zip(['lhs', 'common', 'rhs'],keysplit))

		self.update_node_data(clabel,dict(caches=caches,channels=channels,keysep=keysep))

		return self

	def initialize_pattern(self,pattern):
		parent_obj, mapping = self.initialize_parent(pattern.parent)
		assert len(pattern.helpers)==0, 'Pattern not supported yet.'
		if len(pattern.constraints) == 0:
			self.initialize_pattern_alias(pattern,parent_obj,mapping)
		elif len(pattern.helpers)==0:
			self.initialize_pattern_constraints(pattern,parent_obj,mapping)	
		return self

	def initialize_parent(self,parent):
		# figures out what kind of object parent is
		# initializes it
		# returns the "core" object corresponding to parent
		# and the mapping to child
		if isinstance(parent,GraphContainer):
			mapping,labeling,symmetry_group = canonical_label(parent)
			self.initialize_canonical_label(labeling,symmetry_group)
			parent_obj, mapping = labeling,mapping
		elif isinstance(parent,Pattern):
			self.initialize_pattern(parent)
			parent_obj, mapping = parent, Mapping.create(parent.cache_variables)
		return parent_obj, mapping
			
	def initialize_pattern_alias(self,pattern,parent,mapping):
		cache_ref = self.generate_cache_reference(parent,mapping.reverse()._dict)
		self.add_node_pattern(pattern=pattern,cache=cache_ref,subtype='alias')
		actionmap = {'AddEntry':'AddEntry', 'RemoveEntry':'RemoveEntry'}
		datamap = mapping._dict
		self.add_channel_transform(source=parent,target=pattern,datamap=datamap,actionmap=actionmap)
		return self

	def initialize_pattern_constraints(self,pattern,parent,mapping):
		cache = self.generate_cache(pattern.cache_variables)
		# these are helpers
		caches = {'parent':self.generate_cache_reference(parent,mapping.reverse()._dict)}
		manager = ExecutableExpressionManager(pattern.make_executable_constraints(),pattern.namespace)

		self.add_node_pattern(pattern=pattern,cache=cache,subtype='default',executables=manager,caches=caches)
		actionmap = {'AddEntry':'AddEntry', 'RemoveEntry':'RemoveEntry'}
		datamap = mapping._dict
		self.add_channel_transform(source=parent,target=pattern,datamap=datamap,actionmap=actionmap)

		####
		# process constraints
		filterfn = lambda data,attr: data['attr'] == attr
		actionmap = {'SetAttr':'VerifyEntry'}
		for variable,attr in manager.get_attribute_calls():
			_class = pattern.namespace[variable]
			assert issubclass(_class,BaseClass)
			datamap = {'ref':variable,'attr':'attr'}
			filter_data = partial(filterfn,attr=attr)
			self.add_channel_transform(source=_class,target=pattern,datamap=datamap,actionmap=actionmap,filter_data=filter_data)
			
		# to do: HELPERS
		return self

	def initialize_rule(self,name,rule):
		model_name = '.'.join(name.split('.')[:-1])
		parameters, caches = dict(),dict()
		for param in rule.parameters:
			parameters[param] = f'{model_name}.{param}'
			assert self.get_node(core=f'{model_name}.{param}') is not None
		for pname,pattern in rule.reactants.items():
			self.initialize_pattern(pattern)
			cache_ref = self.get_node(core=pattern).state.cache
			caches[pname] = cache_ref
		rate_law_executable = rule.get_rate_law_executable()
		node_name = f'{name}.propensity'
		self.add_node_variable(
			name = node_name,
			default_value = 0,
			executable = rate_law_executable,
			parameters = parameters,
			caches = caches,
			subtype = 'recompute'
			)
		for k,v in parameters.items():
			self.add_channel_variable_update(source=v,target=node_name,variable=k)
		for pname, pattern in rule.reactants.items():
			self.add_channel_variable_update(source=pattern,target=node_name,variable=pname)

		self.add_channel_variable_update(source=node_name,target='end',variable=node_name)


	def initialize_model(self,model):
		for name,value in model.iter_parameters():
			self.add_node_variable(name,value,subtype='fixed')
		for name,rule in model.iter_rules():
			self.initialize_rule(name,rule)
		return self

	