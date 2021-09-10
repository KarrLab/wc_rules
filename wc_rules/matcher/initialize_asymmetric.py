from ..graph.collections import GraphContainer
from ..graph.canonical_labeling import canonical_label
from ..graph.graph_partitioning import partition_canonical_form
from ..graph.vis import visualize_exprgraph,VisUtil
from ..expressions.exprgraph import FunctionReference, PatternReference
from ..modeling.pattern import Pattern
from ..schema.base import BaseClass

def initialize_start(net):
	net.add_node(core=BaseClass,label=BaseClass)
	return net

def initialize_class(net,_class):
	if _class not in net.nodes:
		net.add_node(core=_class,label=_class)
		parent = _class.__mro__[1]
		net.initialize_class(parent)
		net.add_channel(parent,_class,'discriminate_class')
	return net

def initialize_canonical_form(net,canonical_form,symmetry_group):
	if canonical_form in net.nodes:
		return net
	graph = canonical_form.build_graph_container()
	net.add_node(core=canonical_form,label=canonical_form,symmetry_group=symmetry_group,graph=graph)
	if len(canonical_form.edges) <= 1:
		_class = canonical_form.classes[0]
		net.initialize_class(_class)
		net.add_channel(_class,canonical_form,'initiate_graphbuild')
	else:
		(m1,L1,G1), (m2,L2,G2) = partition_canonical_form(canonical_form,symmetry_group)
		net.initialize_canonical_form(L1,G1)
		net.initialize_canonical_form(L2,G2)
		net.add_channel(L1,canonical_form,'build_graph',mapping=m1)
		net.add_channel(L2,canonical_form,'build_graph',mapping=m2)
	return net

def initialize_pattern(net,pattern,label=None):
	if label is None:
		label = pattern

	if label not in net.nodes:
		net.add_node(core=pattern,label=label)
		rete_node = net.resolve_node(pattern)
		rete_node.data = dict()

		# handle parents
		parent = pattern.parent
		if isinstance(parent,GraphContainer) and len(parent)>0:
			mapping,canonical_form,parent_symmetry_group = canonical_label(parent)
			net.initialize_canonical_form(canonical_form,parent_symmetry_group)
			net.add_channel(canonical_form,pattern,'build_pattern',mapping=mapping)
			graph = parent.duplicate()
		if isinstance(parent,Pattern):
			net.initialize_pattern(parent)
			net.add_channel(parent,pattern,'build_pattern')
			graph = net.resolve_node(parent).data['graph'].duplicate()

		# dict of helper names mapped to rete nodes of helper patterns
		rete_node.data['helpers'] = {}
		for localname,h in pattern.helpers.items():
			net.initialize_pattern(h)
			rete_node.data[localname] = net.resolve_node(h)
			graph.add(PatternReference(id=localname,pattern_id=id(h)))

		# list of executable constraint objects
		rete_node.data['constraints'] = pattern.make_executable_constraints()

		# building extended graph with 
		for x in rete_node.data['constraints']:
			exprgraph = GraphContainer(x.build_exprgraph().get_connected())
			for _,node in exprgraph.iter_nodes():
				if getattr(node,'variable',None) is not None:
					reference = node.variable_reference()
					assert reference in graph._dict
					node.attach_source(graph[reference])
			graph = graph + exprgraph

		graph.validate_connected()
		#VisUtil().write('graph',visualize_exprgraph(graph))
		rete_node.data['graph'] = graph
		
	return net

methods = [
	initialize_start,
	initialize_class,
	initialize_canonical_form,
	initialize_pattern
]