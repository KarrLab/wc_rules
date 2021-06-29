from ..utils.collections import strgen, split_iter, merge_lists
from .collections import CanonicalForm
from .canonical_labeling import canonical_label
from itertools import combinations, repeat, cycle, product
from functools import partial
from collections import defaultdict, Counter,namedtuple
from pprint import pformat
from operator import methodcaller
from copy import deepcopy

def partition_canonical_form(labeling):
	# first construct a line graph from the original graph
	lg_nodes, lg_edges = line_graph(labeling)
	#induced_orbits = induced_orbits(induced_map,groups.orbits())
	# send it to Kernighan/Lin for partitioning
	partition = kernighan_lin(lg_nodes.values(),lg_edges)
	
	# recompute the partitions
	g1, g2 = [deinduce(labeling,lg_nodes,x) for x in partition]
	return canonical_label(g1), canonical_label(g2)


def line_graph(labeling):
	# line graph is a graph where edges have been transformed to nodes
	edges = labeling.edges
	lg_nodes = {y:'e_'+x for x,y in zip(strgen(len(edges)),edges)}
	lg_edges = defaultdict(list)
	for node in labeling.names:
		edges = [x for x in labeling.edges if node in x.nodes()]
		for e1, e2 in combinations(edges,2):
			e1,e2 = sorted([lg_nodes[e] for e in [e1,e2]])
			lg_edges[e1].append(e2)
	return lg_nodes,lg_edges

def induced_orbits(induced_nodes,orbits):
	indexes = dict()
	for i,orb in enumerate(orbits):
		indexes.update(dict(zip(orb,repeat(i))))
	certs = defaultdict(list)
	for edge,induced_node in induced_nodes.items():
		n1,a1,n2,a2 = edge.unpack()
		cert = tuple(sorted([(indexes[n1],a1),(indexes[n2],a2)])) 	
		certs[cert].append(induced_node)
	induced_orbits = list(certs.values())
	return induced_orbits
	
def deinduce(labeling,induced_map,edgelabels):
	edges = tuple([e for e,L in induced_map.items() if L in edgelabels])
	names = tuple(sorted(set(merge_lists([x.nodes() for x in edges]))))
	attrs = tuple(sorted([x for x in labeling.attrs if x.node in names]))
	classes = tuple([labeling.classes[labeling.names.index(x)] for x in names])
	g = CanonicalForm(names,classes,attrs,edges).build_graph_container()
	return g

def kernighan_lin(nodes,edges):
	# nodes is a sorted list of names
	# edges is a dict node: [node node]
	# convert it to a counter
	# (node, node): n_edges

	# Algorithm.
	# Start with an initial partition
	# Keep track of swappable node pairs
	# Greedily choose the best swap in the current available ones
	# Fix the swap, eliminate other swapping choices involving the fixed nodes

	edge_wt = Counter([(k,w) for k,v in edges.items() for w in v])
	partition = split_iter(nodes,2)
	allowed_swaps = list(product(*partition))
	cost = evaluate_cut(partition,edge_wt)
	while allowed_swaps:
		candidates = [implement_swap(partition,swap) for swap in allowed_swaps]
		costs = [evaluate_cut(p,edge_wt) for p in candidates]
		if min(costs) >= cost:
			break
		idx = costs.index(min(costs))
		partition,cost,swap = candidates[idx], costs[idx], allowed_swaps[idx]
		allowed_swaps = filter_swaps(allowed_swaps,swap)
	return partition

def filter_swaps(swaps,swap):
	return [(a,b) for (a,b) in swaps if not any([a in swap,b in swap])]

def implement_swap(partition,swap):
	p = deepcopy(partition)
	idx0, idx1 = p[0].index(swap[0]), p[1].index(swap[1])
	p[0][idx0], p[1][idx1] = p[1][idx1], p[0][idx0]
	return p

def evaluate_cut(partition,edge_wt):
	return sum([edge_wt[tuple(sorted(e))] for e in product(*partition)])