from ..schema.base import BaseClass
from ..utils.random import generate_id
from ..utils.collections import Mapping
from ..graph.graph_partitioning import partition_canonical_form
from ..graph.canonical_labeling import canonical_label
from ..graph.collections import GraphContainer
from collections import deque,Counter
# nodes must be a dict with keys
# 'type','core',
# 'state' gets automatically initialized
# other keys get pushed into **data

def initialize_start(net):
	net.add_node(type='start',core=BaseClass)
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


def initialize_pattern(net,pattern):
	if len(pattern.constraints) == 0:
		parent = pattern.parent
		# is an alias for its parent
		if isinstance(parent,GraphContainer):
			m, L, G = canonical_label(parent)
			net.initialize_canonical_label(L,G)
			net.add_node(type='pattern',core=pattern,symmetry_group=G,parent=L,mapping=m,alias=True)
			net.add_channel(type='alias',source=L,target=pattern,mapping=m)
	return net

def print_merge_form(names,m1,m2):
	s1 = '(' + ','.join(names) + ')'
	s2 = '(' + ','.join(m1.sources) + ')' + '->' + '(' + ','.join(m1.targets) + ')'
	s3 = '(' + ','.join(m2.sources) + ')' + '->' + '(' + ','.join(m2.targets) + ')'
	return s1 + ' <-> (' + s2 + ') + (' + s3 + ')'

default_initialization_methods = [method for name,method in globals().items() if name.startswith('initialize_')]
