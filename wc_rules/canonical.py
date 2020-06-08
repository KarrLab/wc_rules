from functools import partial
from itertools import product
from collections import defaultdict,deque
from pprint import pformat
import math

##### DESCRIPTION ####################
# An ordered partition is a list of cells of nodes of a graph: 
# {de}{abc}{f} is an OP of a graph {abcdef} with edges ad, ae, bd, be, cd, ce, df, ef.
# An OP is "equitable" if each cell's nodes have identical relationships to other cells:
# 	nodes in {de} each have 3 edges to {abc} and 1 to {f}
# 	nodes in {abc} each have 2 edges to {de} 
# 	node in {f} has 2 edges to {de}.
# The coarsest equitable partition CEP == each cell is a node orbit {de}{abc}{f}.
# The finest equitable partition FEP == an ordering of nodes {d}{e}{a}{b}{c}{f}.
# To find CEP, refine an initial deterministically ordered partition until its equitable.
# To find FEP, sequentially break-and-refine cells in a CEP until all cells are singletons.

##### DETAILS ##########################
# index_partition() 
#	input: a partition
#	output: each node receives the index of its cell in the partition
# node_certificate()
#	input: a node, a partition's index, graph
#	output: a certificate characterizing the node's relationship to nodes in other cells
# CertificateCounter(), groups()
# 	input: a list of nodes, a certificate function
#	output: partitions nodes into groups with matching certificates
# partition_cell()
# 	input: a cell in a partition, graph
#	output: breaks the cell into smaller cells if cell nodes have non-matching certificates
# refine_partition()
#	input: initial partition
#	output: sequentially calls partition_cell and reindexing until all cells have matching certificates
# break_and_refine()
# 	input: an partition with at least one non-singleton cell 
# 	output: separates lexicographic leader {abc}->{a},{bc}, refines until equitable,
#	(tracks breaking procedure using a leaders dict a:{bc})
# canonical_ordering()
#	input: graph
#	ouput: CEP (ordered by FEP), leaders


class CertificateCounter(defaultdict):
	def __init__(self,fn,_list):
		super().__init__(list)
		for elem in _list:
			self[fn(elem)].append(elem)

	def groups(self):
		return [self[key] for key in sorted(self)]

####### methods for generating a canonical partition/ordering of a graph container
def canonical_ordering(g):
	# partition = coarsest equitable partition
	partition = refine_partition(g,initial_partition(g))
	p, leaders = partition.copy(), dict()	
	while len(p) < len(g):
		p, leader, remaining = break_and_refine(g,p)
		leaders[leader] = remaining

	order = [x for y in p for x in y]
	#order = canonical ordering
	for x in partition:
		x.sort(key = lambda x: order.index(x))

	return partition,leaders

def break_and_refine(g,p):
	# identify first non-singleton cell idx, 
	# separate its lexicographic leader and call refine_partition
	idx = [i for i,x in enumerate(p) if len(x)>1][0]
	leader, remaining = p[idx][0], p[idx][1:]
	p[idx:idx+1] = [ [leader], remaining ]
	p = refine_partition(g,p)
	return p, leader, remaining  
		

def refine_partition(g,p):
	# g is a graph, p is an ordered partition
	rhs,lhs,modified = deque(p), deque(), False
	indexes = index_partition(rhs)
	while rhs:
		elem = rhs.popleft()
		cells = partition_cell(elem,indexes,g)
		lhs += cells
		if len(cells) > 1:
			indexes, modified  = index_partition(lhs+rhs), True
		if len(rhs)==0 and modified:
			rhs, lhs, modified = lhs, deque(), False
	return list(lhs)

def index_partition(partition):
	# maps each idx in g -> index of cell containing idx in partition
	return dict([(x,i) for i,cell in enumerate(partition) for x in cell])

def partition_cell(cell,indexes,g):
	# returns a singleton deque or a deque further partitioning cell
	if len(cell)==1:
		return deque([cell])
	fn = partial(node_certificate,d=indexes,g=g)
	cert = CertificateCounter(fn,cell)
	return deque( cert.groups() )

def node_certificate(idx,d,g):
	# idx in g -> edges_sorted_by_indexes_of_targets_in_partition
	node = g[idx]
	attrs = node.get_nonempty_related_attributes()
	cert = [(d[x.id],a) for a in attrs for x in node.listget(a)]
	return tuple(sorted(cert))

### methods for seeding the canonical partition algorithm
def initial_partition(g):
	# partition g using initial_node_certificate
	fn = partial(initial_node_certificate,g=g)
	cert = CertificateCounter(fn,sorted(g.keys()))
	return deque( cert.groups() )

def initial_node_certificate(idx,g):
	# idx in g -> <degree, class_name, sorted_edges>
	node = g[idx]
	attrs = node.get_nonempty_related_attributes()
	edges = [(a,x.__class__.__name__) for a in attrs for x in node.listget(a)]	
	return (len(edges),node.__class__.__name__,tuple(sorted(edges)))
