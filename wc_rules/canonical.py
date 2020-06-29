from collections import defaultdict,deque
import math
from itertools import product
from functools import partial
from .indexer import BiMap
from .utils import strgen, concat, printvars
from operator import itemgetter
from sortedcontainers import SortedSet
from dataclasses import dataclass

@dataclass(unsafe_hash=True)
class CanonicalForm:
	partition: tuple
	classes: tuple
	leaders: tuple
	edges: tuple

@dataclass(unsafe_hash=True)
class SymmetryGenerator:
	source: tuple
	targets: tuple
	
def canonical_label(g):
	partition,order,leaders = canonical_ordering(g)
	syms = []
	label_map = BiMap.create(order,strgen(len(order)))
	new_data = {
		'partition': tuple(tuple(x) for x in label_map.replace(partition)),
		'classes': tuple(g[x].__class__ for x in order),
		'leaders': tuple(sorted(label_map.replace(leaders))),
		'edges': tuple(SortedSet(relabel_edge(e,label_map) for e in collect_edges(g)))
	}

	return CanonicalForm(*new_data.values())


def relabel_edge(edge,label_map):
	(x,a),(y,b) = edge
	x1,y1 = sorted(map(label_map.replace, [x,y]))
	return tuple([(x1,a),(y1,b)])

def collect_edges(g):
	for node in g:
		for attr in node.get_nonempty_related_attributes():
			related_attr = node.get_related_name(attr)
			for related_node in node.listget(attr):
				yield (node.id, attr), (related_node.id,related_attr)
	return 
def canonical_edges(g,label_map):
	edges = SortedSet()
	for node in g:
		for attr in node.get_nonempty_related_attributes():
			related_attr = node.get_related_name(attr)
			for related_node in node.listget(attr):
				edge = tuple(sorted( [(node.id,attr), (related_node.id,related_attr)] ))
				edges.add(edge)
	return tuple(edges)

def compute_symmetry_generators(g,partition,order):
	# Key Idea: Within each node orbit in the partition, 
	# one can map the leader to itself or to another node (second-leader).
	# This choice creates a bifurcation in the search tree for generators.
	generators,candidates = SortedSet(), deque([copy_partition(partition)])
	while candidates:
		L = candidates.popleft()
		if len(L) == len(g):
			generators.add(tuple(concat(L)))
			continue
		A = break_and_refine(g,	copy_partition(L))[0]
		B = break_and_refine(g, swap_leaders(L))[0]
		candidates.extend([A, B])
	return SymmetryGenerator(order,generators)

def compute_symmetries(generator_object):
	# Key Idea: A generator produces symmetries in two ways.
	# A cyclic group by self-applying the generator as many times as needed.
	# A coset by composing its cyclic group with an existing set of symmetries.
	symmetries = SortedSet()
	generators = [BiMap.create(generator_object.source,x) for x in generator_object.targets]
	for x in generators:
		cycle = generate_cycle_group(x)
		coset = generate_cartesian_product(symmetries,cycle)
		symmetries.update(cycle,coset)
	return list(symmetries)

def swap_leaders(partition):
	idx, R = first_nontrivial_cell(partition), copy_partition(partition)
	R[idx][0], R[idx][1] = R[idx][1], R[idx][0]
	return R
	
def generate_cycle_group(generator):
	cycle_group, x = SortedSet(), generator
	while x not in cycle_group:
		cycle_group.add(x)
		x = generator*x
	return list(cycle_group)

def generate_cartesian_product(X,Y):
	return [x*y for x in X for y in Y]

def copy_partition(partition):
	return [x.copy() for x in partition]

##### DESCRIPTION OF CANONICAL ORDERING ALGORITHM ####################
# Definitions: (a) An ordered partition (OP) partitions a graph's nodes into ordered cells.
# (b) A node certificate (NC) for a node characterizes its edges to each cell in an OP.
# (c) An equitable partition (EP) is an OP where each cell's nodes have identical NCs.
# (d) A coarsest EP (CEP) is an EP with the least number of cells. Equivalent to a node orbit partition.
# (e) A finest EP (FEP) is an EP with the most number of cells. Equivalent to a node ordering.
#
# # Canonical ordering procedure:
# input: 
#	graph G, initial deterministic OP
# procedure:
#	CEP <- refine OP till equitable
# 	FEP <- break and refine CEP 
# output:
# 	orbits = CEP, order = FEP, leaders = lexicographic leaders used to break CEP
#
# Example: 
# input:
#	an undirected square graph with nodes a,b,c,d
#	an initial deterministic OP {a,b,c,d}
# procedure:
#	{a,b,c,d} --refine--> {a,b,c,d} a CEP
# 	{a,b,c,d} --break(a)--> {a}{b,c,d} --refine--> {a}{b,c}{d}
# 	{a}{b,c}{d} --break(b)--> {a}{b}{c}{d} --refine--> {a}{b}{c}{d} a FEP
# output:
#	orbits = {a,b,c,d}
#	order = {a}{b}{c}{d}
#	leaders = a->{b,c,d}, b->{c}
#
# # Helper methods
#	compute node certificates
#		given OP, for each node, count number and type
#		of edges to "any" node in cell i for all cells i.
#	refine partition
#		given OP, iteratively compute certificates on non-singleton cells,
# 		and subdivide them if multiple certificate values detected.
#	break and refine: 
#		given CEP, separate lexicographic leader into its own cell,
#		then call refine.

####### methods for generating a canonical partition/ordering of a graph container
def canonical_ordering(g):
	# partition = coarsest equitable partition
	partition = refine_partition(g,initial_partition(g))
	p, leaders = partition.copy(), list()	
	while len(p) < len(g):
		p, leader, remaining = break_and_refine(g,p)
		leaders.extend([(leader,x) for x in remaining])
		
	order = [x for y in p for x in y]
	#order = canonical ordering
	for x in partition:
		x.sort(key = lambda x: order.index(x))

	return partition, order, leaders

def break_and_refine(g,p):
	# identify first non-singleton cell idx, 
	# separate its lexicographic leader and call refine_partition
	idx = first_nontrivial_cell(p)
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

# methods to index and create partitions
def first_nontrivial_cell(partition):
	return [i for i,x in enumerate(partition) if len(x)>1][0]

def index_partition(partition):
	# maps each idx in g -> index of cell containing idx in partition
	return dict([(x,i) for i,cell in enumerate(partition) for x in cell])

def partition_cell(cell,indexes,g):
	# returns a singleton deque or a deque further partitioning cell
	return deque( group_by_node_certificates(node_certificate,cell,d=indexes,g=g) )

def initial_partition(g):
	# returns an initial partition of nodes of g
	return deque( group_by_node_certificates(initial_node_certificate, sorted(g.keys()), g=g) )

# methods to compute certificates and sort and group nodes by certificates	
def node_certificate(idx,d,g):
	# idx in g -> edges_sorted_by_indexes_of_targets_in_partition
	node = g[idx]
	attrs = sorted(node.get_nonempty_related_attributes())
	cert = [(d[x.id],a) for a in attrs for x in node.listget(a)]
	return tuple(sorted(cert))
	
def initial_node_certificate(idx,g):
	# idx in g -> <degree, class_name, sorted_edges>
	node = g[idx]
	attrs = sorted(node.get_nonempty_related_attributes())
	edges = [(a,x.__class__.__name__) for a in attrs for x in node.listget(a)]	
	return (-len(edges),node.__class__.__name__,tuple(sorted(edges)))

def group_by_node_certificates(certificate_function,elems,**kwargs):
	if len(elems)==1:
		return [elems]
	x = defaultdict(list)
	for elem in elems:
		x[certificate_function(elem,**kwargs)].append(elem)
	groups = [x[key] for key in sorted(x)]
	return groups

