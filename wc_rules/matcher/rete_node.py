from ..schema.base import BaseClass
from collections import deque
from itertools import dropwhile

from ..graph.graph_partitioning import partition_canonical_form
from frozendict import frozendict

class ReteNode:

	def __init__(self,core=None,**data):
		self.core = core
		self.data = frozendict(data) if data else None
		self.slots = deque()
		self.cache = None

def initialize_start(net):
	net.add_node(ReteNode('start'))
	return net

def initialize_base_subclass(net,_class):
	classes = ['start'] + list(reversed(_class.__mro__[:_class.__mro__.index(BaseClass)]))
	classpairs = [(c1,c2) for c1,c2 in zip(classes[:-1],classes[1:]) if c2 not in net.nodes]
	for c1,c2 in classpairs:
		net.add_node(ReteNode(c2))
		n1,n2 = [net.nodes[x] for x in [c1,c2]]
		net.add_channel(n1,n2,'passthrough')
	return net

def initialize_single_edge(net,canonical_form,group):
	assert len(canonical_form.edges)==1
	_class = min(canonical_form.classes,key=lambda c: len(c.__mro__))
	if _class not in net.nodes:
		net.initialize_base_subclass(_class)
	net.add_node(ReteNode(canonical_form,group=group))
	n1,n2 = [net.nodes[x] for x in [_class,canonical_form]]
	net.add_channel(n1,n2,'passthrough')
	return net

def initialize_canonical_form(net,canonical_form,group):
	if canonical_form in net.nodes:
		return net
	assert len(canonical_form.edges) >= 1
	if len(canonical_form.edges)==1:
		net.initialize_single_edge(canonical_form,group)
		return net
	net.add_node(ReteNode(canonical_form,group=group))
	for mapping,labeling,grouping in partition_canonical_form(canonical_form,group):
		net.initialize_canonical_form(labeling,grouping)
		n1,n2 = [net.nodes[x] for x in [labeling,canonical_form]]
		net.add_channel(n1,n2,'merge',mapping=mapping)
	return net

def initialize_pattern(net,pattern,group):
	return net

def initialize_rule(net,rule):
	return net

def initialize_RBM(net,rbm):
	return net

initializers = [
	initialize_start,
	initialize_base_subclass,
	initialize_single_edge,
	initialize_canonical_form
]
