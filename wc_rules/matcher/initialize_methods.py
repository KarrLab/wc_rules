from ..schema.base import BaseClass
from ..modeling.pattern import Pattern, GraphContainer
from ..utils.collections import UniversalSet, triple_split
from .token import TokenTransformer
from ..graph.graph_partitioning import partition_canonical_form
from ..graph.canonical_labeling import canonical_label
from ..graph.permutations import Mapping
from functools import partial
from attrdict import AttrDict
from collections import ChainMap

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

		if self.get_node(core=pattern) is not None:
			return self

		# Approach
		# If it requires a parent, initialize parent, and parent-pattern channel
		#	subcase: if no constraints, it is an alias. Initialize and exit.
		# If it requires helpers, initialize helpers, links to helper caches
		# Create executable expression manager
		# collect attribute calls, create attr-transform channels for each attr
		# collect helper function calls, create entry-transform channels
		# for each unique kwarg setting

		caches = dict()
		
		# If it requires a parent pattern/graphcontainer
		# initialize parent, create the channel from parent to current pattern
		requires_parent = (isinstance(pattern.parent,GraphContainer) and len(pattern.parent)) or isinstance(pattern.parent,Pattern)

		if requires_parent:
			if isinstance(pattern.parent,GraphContainer):
				mapping, parent, symmetry_group = canonical_label(pattern.parent)
				self.initialize_canonical_label(parent,symmetry_group)
			elif isinstance(pattern.parent,Pattern):
				self.initialize_pattern(pattern.parent)
				parent, mapping = pattern.parent, Mapping.create(pattern.parent.cache_variables)
			actionmap, datamap= {'AddEntry':'AddEntry', 'RemoveEntry':'RemoveEntry'}, mapping._dict
			self.add_channel_transform(source=parent,target=pattern,datamap=datamap,actionmap=actionmap)
			caches['parent'] = self.generate_cache_reference(parent,mapping.reverse()._dict)

			if len(pattern.constraints)==0:
				# TODO: use cache = DatabaseAlias(caches['parent']) instead of cache = caches['parent']
				self.add_node_pattern(pattern=pattern,cache = caches['parent'],subtype ='alias',caches=caches)
				return self

		for var,pat in pattern.helpers.items():
			self.initialize_pattern(pat)
			caches[var] = self.get_node(core=pat).state.cache

		manager = pattern.make_executable_expression_manager()

		if requires_parent:
			self.add_node_pattern(pattern=pattern,subtype='default',executables=manager,caches=caches)

		for variable, attr in manager.get_attribute_calls():
			assert issubclass(pattern.namespace[variable],BaseClass)
			self.add_channel_transform(
				source = pattern.namespace[variable],
				target = pattern,
				datamap = {'ref':variable,'attr':'attr'},
				actionmap = {'SetAttr':'VerifyEntry'},
				filter_data = partial(lambda data,attr: data['attr'] == attr, attr=attr)
			)

		for p,kwargs in manager.get_helper_calls():
			self.add_channel_transform(
				source = pattern.helpers[p],
				target = pattern,
				datamap = dict(kwargs),
				actionmap = {'AddEntry':'VerifyEntry','RemoveEntry':'VerifyEntry'}
			)

		return self

	def initialize_rule(self,name,rule):
		model_name = '.'.join(name.split('.')[:-1])
		parameters, caches = dict(),dict()
		for param in rule.parameters:
			parameters[param] = f'{model_name}.{param}'
			assert self.get_node(core=f'{model_name}.{param}') is not None, f'Cannot find {model_name}.{param}'
		for pname,pattern in ChainMap(rule.reactants,rule.helpers).items():
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
		self.function_node_variable(self.get_node(core=f'{name}.propensity'),token={})
	
	def initialize_rules(self,rules,parameters):
		for name,value in parameters.items():
			self.add_node_variable(name,value,subtype='fixed')
		for name,rule in rules.items():
			self.initialize_rule(name,rule)
		return self

	def initialize_observable(self,name,observable):
		caches = dict()
		for pname,pattern in observable.helpers.items():
			self.initialize_pattern(pattern)
			caches[pname]= self.get_node(core=pattern).state.cache
		self.add_node_variable(
			name = name,
			default_value = observable.default,
			executable = observable.make_executable(),
			caches = caches,
			subtype = 'recompute'
			)
		for pname,pattern in observable.helpers.items():
			self.add_channel_variable_update(source=pattern,target=name,variable=pname)
		self.add_channel_variable_update(source=name,target='end',variable=name)
		self.function_node_variable(self.get_node(core=name),token={})
		return self

	def initialize_observables(self,observables):
		for name,obs in observables.items():
			self.initialize_observable(name,obs)
		return self