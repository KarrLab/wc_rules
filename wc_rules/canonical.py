from collections import defaultdict,deque
import math
from itertools import product
from functools import partial
from .indexer import BiMap
from .utils import strgen, concat, printvars
from operator import itemgetter
from sortedcontainers import SortedSet



def canonical_label(g):
	partition,order,leaders = canonical_ordering(g)
	syms = compute_symmetries(g,partition,order)

	
	#v = BiMap.create(order,strgen(len(order)))
	#print(partition)
	#print(v)
	return partition,leaders

def compute_symmetries(g,partition,order):
	# input: canonical partition, empty generator set
	# make a stack with initial element being the canonical partition
	# at each step, pick a candidate from the stack and do:
	# 	check if fully refined, if so update generator set
	#	else, make two copies of the partition
	#		first one is intact, second one swaps leaders of first non-trivial cell
	#		e.g. [x][abc][d] -> [x][abc][d], [x][bac][d]
	#		run break-and-refine on the copies 
	#		update stack with the generated partitions
	# output: set of generators

	# input: set of generators, empty set of symmetries
	# for each generator, 
	#	generate cyclic group by self applying the generator on itself
	#	generate group product by applying each elem of cyclic group to each elem of existing symmetries
	#	update symmetries from both cyclic group and coset group
	# output: set of all symmetries

	generators,candidates = SortedSet(), deque([copy_partition(partition)])
	while candidates:
		L = candidates.popleft()
		if len(L) == len(g):
			generators.add(tuple(concat(L)))
			continue
		A = break_and_refine(g,	copy_partition(L))[0]
		B = break_and_refine(g, swap_leaders(L))[0]
		candidates.extend([A, B])

	symmetries = SortedSet()
	for x in generators:
		perm = BiMap.create(order,x)
		cycle_group = generate_cycle_group(perm)
		cartesian_product = generate_cartesian_product(symmetries,cycle_group)
		symmetries.update(cycle_group,cartesian_product)
			
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
# The canonical ordering algorithm sorts nodes by some initial deterministic order,
# computes CEP, then FEP, while tracking lexicographic leaders that were used to break ties.
# The outputs are CEP, FEP, leaders

##### DETAILS ##########################
# index_partition() 
#	input: a partition
#	output: each node receives the index of its cell in the partition
# node_certificate()
#	input: a node, a partition's index, graph
#	output: a certificate characterizing the node's relationship to nodes in other cells
# group_by_node_certificates()
# 	input: a list of nodes, a certificate function, additional kwargs for certfn.
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

