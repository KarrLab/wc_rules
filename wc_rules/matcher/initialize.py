from ..schema.base import BaseClass
from ..utils.random import generate_id
from ..utils.collections import Mapping, quoted, unzip, invert_dict, subdict
from ..expressions.exprgraph import PatternReference, ParameterReference
from ..graph.graph_partitioning import partition_canonical_form
from ..graph.canonical_labeling import canonical_label
from ..graph.collections import GraphContainer
from ..modeling.pattern import Pattern
from collections import deque,Counter, defaultdict, ChainMap
from attrdict import AttrDict
# nodes must be a dict with keys
# 'type','core',
# 'state' gets automatically initialized
# other keys get pushed into **data

def initialize_start(net):
	net.add_node(type='start',core=BaseClass)
	return net

def initialize_end(net):
	net.add_node(type='end',core='end')
	net.get_node(type='end').state.cache = deque()
	return net

def initialize_class(net,_class):
	if net.get_node(core=_class) is not None:
		return net
	net.add_node(type='class',core=_class)
	parent = _class.__mro__[1]
	net.initialize_class(parent)
	net.add_channel(type='pass',source=parent,target=_class)
	return net

def initialize_collector(net,source,label):
	idx = f'collector_{label}'
	net.add_node(type='collector',core=idx)
	net.get_node(type='collector',core=idx).state.cache = deque()
	net.add_channel(type='pass',source=source,target=idx)
	return net

def initialize_canonical_label(net,clabel,symmetry_group):

	if net.get_node(core=clabel) is not None:
		return net

	if len(clabel.names)<=2 and net.get_node(core=clabel) is None:
		# it is a graph with a single node or single edge
		net.initialize_class(clabel.classes[0])
		net.add_node(type='canonical_label',core=clabel,symmetry_group=symmetry_group)
		net.initialize_cache(clabel,clabel.names)
		chtype = {1:'node',2:'edge'}[len(clabel.names)]
		mapping = {1:Mapping(['idx'],['a']),2:Mapping(['idx1','idx2'],['a','b'])}[len(clabel.names)]
		net.add_channel(type=f'transform_{chtype}_token',source=clabel.classes[0],target=clabel,mapping=mapping)		

	else:
		# it is a graph with atleast 2 edges
		(m1,L1,G1), (m2,L2,G2) = partition_canonical_form(clabel,symmetry_group)
		#print(print_merge_form(clabel.names,m1,m2))
		net.initialize_canonical_label(L1,G1)
		net.initialize_canonical_label(L2,G2)
		net.add_node(type='canonical_label',core=clabel,symmetry_group=symmetry_group)
		net.initialize_cache(clabel,clabel.names)
		net.add_channel(type='merge',source=L1,target=clabel,mapping=m1)
		net.add_channel(type='merge',source=L2,target=clabel,mapping=m2)
	return net


def initialize_pattern(net,pattern,parameters = dict()):

	if net.get_node(core=pattern) is not None:
		return net

	# handle helpers
	helpers = dict()
	if len(pattern.helpers) > 0:
		for var,p in pattern.helpers.items():
			net.initialize_pattern(p)
			helpers[var] = p
	
	# handle parent
	parent,constraints = pattern.parent, pattern.constraints
	if isinstance(parent,GraphContainer):
		parent,attrs = parent.strip_attrs()
		constraints = [f'{var}.{attr} == {quoted(value)}' for var in attrs for attr,value in attrs[var].items()] + constraints
		m, L, G = canonical_label(parent)
		net.initialize_canonical_label(L,G)
		pdict = AttrDict(parent=L,mapping=m,symmetry_group=G)
	elif isinstance(parent,Pattern):
		net.initialize_pattern(parent)
		m = Mapping.create(parent.variables)
		G = net.get_node(core=parent).data.symmetry_group
		pdict = AttrDict(parent = parent, mapping=m, symmetry_group=G)
	else:
		assert False, f'Some trouble initializing parent from {parent}'

	graph = parent.duplicate() if isinstance(parent,GraphContainer) else net.get_node(core=parent).data.exprgraph
	constraint_objects = []
	if len(constraints) == 0:
		# is an alias for its parent
		net.add_node(type='pattern',core=pattern,symmetry_group=pdict.symmetry_group,exprgraph = graph,alias=True)
		net.add_channel(type='alias',source=pdict.parent,target=pattern,mapping=pdict.mapping)
		parent_wrapper = net.get_node(core=pdict.parent).wrapper
		child_wrapper = net.get_node(core=pattern).wrapper
		child_wrapper.set(target=parent_wrapper,mapping=pdict.mapping)
		
	if len(constraints) > 0:
		
		for var,p in helpers.items():
			graph.add(PatternReference(id=var,pattern_id=id(p)))
		for param in parameters:
			graph.add(ParameterReference(id=param,parameter_name=param))
		for c in constraints:
			x = pattern.make_executable_constraint(c)
			exprgraph = GraphContainer(x.build_exprgraph().get_connected())
			for _,node in exprgraph.iter_nodes():
				if getattr(node,'variable',None) is not None:
					reference = node.variable_reference()
					assert reference in graph._dict, f'{reference} not found'
					node.attach_source(graph[reference])
			constraint_objects.append(x)
			
			graph = graph + exprgraph
		m,L,G = canonical_label(graph)
		symmetry_group = G.duplicate(m).restrict(pattern.variables)
		
		# collect update channels
		constraint_pattern_relationships = set()
		constraint_attr_relationships = set()
		for x in constraint_objects:
			for fname_tuple in x.deps.function_calls:
				varname = fname_tuple[0]
				if varname in pattern.variables and isinstance(pattern.namespace[varname],type) and issubclass(pattern.namespace[varname],BaseClass):
					fname = fname_tuple[1]
					fn = getattr(pattern.namespace[varname],fname)
					if getattr(fn,'_is_computation',False):
						attrs = pattern.namespace[varname]().get_attrdict(ignore_id=True,ignore_None=False,use_id_for_related=False).keys()
						kws = (set(fn._kws) - set(x.deps.function_calls[fname_tuple]['kws'])) & set(attrs)
						for kw in kws:
							constraint_attr_relationships.add((x,varname,kw,))
				if varname in helpers:
					kwpairs = x.deps.function_calls[fname_tuple]['kwpairs']
					kwpairs = [(x,y) for x,y in kwpairs if x in helpers[varname].variables and y in pattern.variables]
					m = Mapping.create(*unzip(kwpairs)) if kwpairs else None
					constraint_pattern_relationships.add((x,varname,m,))
			for var, attrs in x.deps.attribute_calls.items():
				for attr in attrs:
					if var in pattern.variables:
						constraint_attr_relationships.add((x,var,attr,))

		
		helper_channels = set([(pname,mapping) for _,pname,mapping in constraint_pattern_relationships])
		attr_channels = set([(var,attr) for _,var,attr in constraint_attr_relationships])	

		#print(constraint_pattern_relationships)
		#print(constraint_attr_relationships)
		resolved_helpers = {h:net.get_node(core=helpers[h]).wrapper for h in helpers}
		net.add_node(type='pattern',core=pattern,symmetry_group=symmetry_group,exprgraph=graph,helpers=resolved_helpers,constraints=constraint_objects,parameters=parameters)
		names = [x for x in pattern.namespace if isinstance(pattern.namespace[x],type) and issubclass(pattern.namespace[x],BaseClass)]
		net.initialize_cache(pattern,names)
		net.add_channel(type='parent',source=pdict.parent,target=pattern,mapping=pdict.mapping)

		for pname, mapping in helper_channels:
			net.add_channel(type='update_pattern',source=helpers[pname],target=pattern,mapping=mapping)

		for var,attr in attr_channels:
			varclass = pattern.namespace[var]
			literal_attrs = varclass().get_literal_attributes(ignore_id=True,ignore_None=False)
			txt = 'idx' if attr in literal_attrs else 'idx1'
			mapping = Mapping.create([txt],[var])
			net.initialize_class(varclass)
			net.add_channel(type='update_pattern',source=varclass,target=pattern,mapping=mapping,attr=attr)

	return net

def initialize_rule(net,rule,name,parameters=dict()):
	if net.get_node(core=name) is not None:
		return net

	propensity = rule.get_rate_law_executable()	
	affects_propensity = []

	for var,p in ChainMap(rule.reactants,rule.helpers).items():
		net.initialize_pattern(p, parameters = subdict(parameters,p.parameters))
		if var in propensity.keywords:
			affects_propensity.append(p)

	reactants = {var:net.get_node(core=p).wrapper for var,p in rule.reactants.items()}
	helpers = {var:net.get_node(core=p).wrapper for var,p in rule.helpers.items()}

	actions = rule.get_action_executables()
	
	net.add_node(type='rule',core=name,reactants=reactants,helpers=helpers,propensity=propensity,parameters=parameters,actions=actions)
	for p in affects_propensity:
		net.add_channel(type='update_rule',source=p,target=name)

	fn = lambda rule_node: rule_node.state.cache
	net.add_channel(type='update_variable',source=name,target='end',name=name,fn=fn,vartype='rule_propensity')
	return net

	
	
def print_merge_form(names,m1,m2):
	s1 = '(' + ','.join(names) + ')'
	s2 = '(' + ','.join(m1.sources) + ')' + '->' + '(' + ','.join(m1.targets) + ')'
	s3 = '(' + ','.join(m2.sources) + ')' + '->' + '(' + ','.join(m2.targets) + ')'
	return s1 + ' <-> (' + s2 + ') + (' + s3 + ')'

default_initialization_methods = [method for name,method in globals().items() if name.startswith('initialize_')]
