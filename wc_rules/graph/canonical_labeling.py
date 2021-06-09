from ..utils.collections import invert_dict, accumulate, listmap, tuplify, merge_lists, remap_values
from collections import deque, Counter
from sortedcontainers import SortedDict, SortedList
from .permutations import Permutation
from copy import deepcopy

# Implements ISMAGS PLoS One 2014 (Houbraken et al.) Fig 4
# DEFINITIONS
# Ordered partition
#	an ordered partition of the nodes of the graph. Each element is called a cell.
#	e.g., (a|bcd)
# Initial deterministic partition
# 	Cells are initially sorted by degree, class, literal attributes, 
#	And internally sorted by node labels.
# Ordered partition pair (OPP)
#	A pair of partitions which implies a "pairing" between corresponding nodes and cells.
# 	E.g.,
#	(a|bcd)    (a|bcd)
#	(a|bcd) or (a|cbd)
# Refining a partition
#	Break up the cells into smaller cells so that
# 	Elements of a cell have identical same edge-relationships to elements of other cells
#	E.g., (a|bcd) -> (a|b|cd) or (a|b|c|d), whichever has the above property.
# Mapping Options
#	For the first non-trivial cell of the OPP
#	The lexicographic leader in the top partition can be mapped
#	To each element in the bottom partition
#	E.g.,
#	(a|bcd)    (a|bcd)    (a|bcd)
#	(a|bcd)    (a|cbd)    (a|dbc)
# Switch-and-Split
#	For the first non-trivial cell of the OPP
#	Given a mapping option (source->target)
# 	Create a separate cell for the source in the top partition
#	Create a separate cell for the target in the bottom partition
#   E.g., for the mapping option b->c
#	(a|bcd)    (a|b|cd)
#	(a|cbd) -> (a|c|bd) 
# Search tree
# Search tree nodes consist of successively refined OPPs
# Search tree edges consist of mapping options

# Symmetry finding Procedure:
# Create a seed OPP with an initial deterministic partition, mapping every element to itself
# DFS explore the search tree:
# 	For each non-trivial cell
# 	Identify the mapping options
# 	Use them to switch-and-split then refine
# Outputs should be a list of fully refined OPPs with differing bottom partitions.
# e.g.,
#	(a|b|c|d)    (a|b|c|d)
#	(a|b|c|d) ,  (a|c|b|d) , etc.
# These are symmetries of the graph. 
#
# Orbit-pruning improvement:
# Since we explore the search tree by DFS,
# Once we find a permutation, we can update our idea of what are the node orbits of the graph.
# Then, any other subsequent attempt to pair nodes within the same orbit can be ignored.
# E.g., once we identify permutations (a)(bc)(d) and (a)(b)(cd), 
# we know {b,c,d} are in the same orbit and we can ignore any future mapping option b->d.
# The symmetries produced are then considered "generators" of the full symmetry set.

# Safety checks
# The first symmetry produced must be the identity symmetry.
# Without orbit pruning, each valid symmetry must be produced only once.
# With orbit pruning, the symmetries produced must be sufficient to generate the full set.

def canonical_label(g):
	partition = initialize_partition(g)
	opp = ordered_partition_pair(partition,partition)
	orbindex = initialize_orbindex(partition)
	search_tree = deque([search_tree_element(opp)])
	generators = []

	# convention: 
	# if source,target==None, then 
	# 	we are at a node of the search tree, 
	# 	we either decide to terminate or 
	#	create branching options based on the first non-trivial cell
	# if source,target != None, then 
	# 	we are examining a branching option
	# 	so we must prune, switch-and-split, refine
	# appendleft + reversing mapping options ensures DFS
	while search_tree:
		opp, source, target = search_tree.popleft()
		if source == target == None:
			idx = first_nontrivial_cell(opp)
			if idx is not None:
				# create branching options
				for source, target in mapping_options(opp,idx):
					search_tree.appendleft(search_tree_element(deepcopy(opp),source,target))
			else:
				# terminal node of search tree
				gen = make_permutation(opp)
				generators.append(gen)
				# update orbindex
				orbindex = update_orbindex(orbindex,gen)
		else:
			# prune with orbindex
			if source == target or orbindex[source] != orbindex[target]:
				# execute branching option and refine
				opp = switch_and_split(opp,source,target)
				opp = [refine_partition(p,g) for p in opp]
				search_tree.appendleft(search_tree_element(opp))
	
	for gen in generators:
		print(gen.cyclic_form(simple=True))

# Search tree
def search_tree_element(opp,source=None,target=None):
	return (opp,source,target)

def mapping_options(opp,idx):
	# map leader of opp[0][idx] to each element in opp[1][idx]
	# reversed to give first element top priority in DFS
	return reversed([(opp[0][idx][0],t) for t in opp[1][idx]])

def switch_and_split(opp,source,target):
	idx = first_nontrivial_cell(opp)
	opp[0][idx].remove(source)
	opp[1][idx].remove(target)
	opp[0].insert(idx,[source])
	opp[1].insert(idx,[target])
	return opp

def make_permutation(opp):
	return Permutation.create(merge_lists(opp[0]), merge_lists(opp[1]))

####### Ordered Partition Pair
def ordered_partition_pair(p1,p2):
	return [deepcopy(p1),deepcopy(p2)]

def first_nontrivial_cell(opp):
	idxs = [i for i,x in enumerate(opp[0]) if len(x)>1]
	if idxs:
		return idxs[0]
	return None

def has_nontrivial_cell(opp):
	return first_nontrivial_cell(opp) is not None

###### Partitions
def vis_opp(opp):
	return ''.join(['(' + '|'.join([''.join(x) for x in p]) + ')' for p in opp])

def initialize_partition(g):
	partition = group_by_certificate(initial_certificate,g.variables,g=g)
	partition = refine_partition(partition,g)
	return partition

def refine_partition(partition,g):
	indexes = index_partition(partition)
	while True:
		partition = merge_lists([refine_cell(cell,indexes,g) for cell in partition])
		new_indexes = index_partition(partition)
		if new_indexes == indexes:
			break
		indexes = new_indexes
	return partition

def index_partition(partition):
	return dict([(x,i) for i,gr in enumerate(partition) for x in gr])

def refine_cell(cell,indexes,g):
	groups = group_by_certificate(edge_certificate,cell,indexes=indexes,g=g)
	return groups

######### Orbindex
def initialize_orbindex(partition):
	return {v:k for k,v in enumerate(merge_lists(partition))}

def update_orbindex(orbindex,gen):
	for cyc in gen.cyclic_form():
		if len(cyc)>1:
			nums = [orbindex[x] for x in cyc]
			keys = [x for x in orbindex if orbindex[x] in nums]
			for key in keys:
				orbindex[key] = min(nums)
	return orbindex
	
####### Certification of nodes
def initial_certificate(idx,g):
	x = g[idx]
	cert = (-x.degree(), x.__class__, tuple(sorted(x.iter_literal_attrs())))
	return cert

def edge_certificate(idx,indexes,g):
	x,certs = g[idx], deque()
	for a, nodes in accumulate(x.iter_edges()).items():
		ids = tuple(sorted(Counter(indexes[x.id] for x in nodes).items()))
		certs.append((a,ids,))
	return tuple(sorted(certs))

def group_by_certificate(fn,elems,**kwargs):
	certs = {elem:fn(elem,**kwargs) for elem in elems}
	groups = [sorted(x) for x in list(SortedDict(invert_dict(certs)).values())]
	return groups

	
	