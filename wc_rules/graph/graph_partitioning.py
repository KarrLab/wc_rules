from ..utils.collections import strgen, split_iter, merge_lists, invert_dict
from .collections import CanonicalForm, Mapping
from .canonical_labeling import canonical_label
from itertools import combinations, product
from collections import Counter, ChainMap
from copy import deepcopy

def partition_canonical_form(labeling,group):
	# construct a line graph from the original graph
	# 	see https://en.wikipedia.org/wiki/Line_graph
	# partition it using Kernighan/Lin
	# reconstruct the halves of the original graph

	# trivial case: at most one edge, cannot subdivide further
	if len(labeling.edges) <= 1:
		return None,None

	lg_nodes, lg_edges,lg_orbits = line_graph(labeling.names,labeling.edges,group.orbits())
	partition = kernighan_lin(lg_nodes.values(),lg_edges,lg_orbits)
	g1, g2 = [deinduce(labeling,lg_nodes,x) for x in partition]
	CL1, CL2 = [canonical_label(x) for x in [g1,g2]]
	return CL1,CL2

def partition_until_edge(labeling,group,examined=set(),partitions=[]):
	# input: canonically labeled graph
	# repeatedly partition with partition_canonical_form until you obtain single-edge graphs
	# output: examined set of labels (hashed versions), successive partitions of the graph
	CL1, CL2 = partition_canonical_form(labeling,group)
	if CL1 is None:
		return examined,partitions
	m1,L1,G1 = CL1
	m2,L2,G2 = CL2

	arrow = "\u2192"
	g = labeling.build_graph_container()
	m1 = Mapping.create(m1.sources,[f"{s}{arrow}{t}" for s,t in zip(m1.sources,m1.targets)])
	g1 = L1.build_graph_container(m1)
	m2 = Mapping.create(m2.sources,[f"{s}{arrow}{t}" for s,t in zip(m2.sources,m2.targets)])
	g2 = L2.build_graph_container(m2)
	examined.add(labeling)
	partitions.append((g,g1,g2,))

	if L1 not in examined and len(L1.edges)>1:
		examined,partitions = partition_until_edge(L1,G1,examined,partitions)
	if L2 not in examined and len(L1.edges)>1:
		examined,partitions = partition_until_edge(L2,G2,examined,partitions)

	return examined,partitions

def recompose(m1,L1,m2,L2):
	L11 = L1.remap(m1._dict)
	L21 = L2.remap(m2._dict)
	# names classes attrs edges
	names = tuple(sorted(set(L11.names + L21.names)))
	classesdict = ChainMap(dict(zip(L11.names,L11.classes)), dict(zip(L21.names,L21.classes)))
	classes = tuple([classesdict[x] for x in names])
	attrs = tuple(sorted(set(L11.attrs + L21.attrs)))
	edges = tuple(sorted(set(L11.edges + L21.edges)))
	big_L = CanonicalForm(names,classes,attrs,edges)
	big_g = big_L.build_graph_container()
	return canonical_label(big_g)


def line_graph(nodes,edges,orbits):
	# nodes is a list of names
	# edges is a list of Edge tuples
	# orbits is a partition of nodes

	# line graph is a graph where edges have been transformed to nodes
	# lg_nodes: every edge from labeling.edges mapped to a name
	# lg_edges: a Counter of "interactions" between pairs of lg_nodes
	#	an "interaction" exists if the corresponding original edges share a node
	# lg_orbits: orbits on lg_nodes induced by node orbits
	labels = ['e_'+x for x in strgen(len(edges))]
	lg_nodes = dict(zip(edges,labels))
	lg_edges = Counter()
	for node in nodes:
		local_edges = [lg_nodes[e] for e in edges if node in e.nodes()]
		lg_edges.update(combinations(local_edges,2))

	certs = dict()
	orbindex = {n:i for i,orb in enumerate(orbits) for n in orb}
	for e,L in lg_nodes.items():
		n1,a1,n2,a2 = e.unpack()
		certs[L] = tuple(sorted([(orbindex[n1],a1),(orbindex[n2],a2)]))
	lg_orbits = invert_dict(certs).values()
	return lg_nodes,lg_edges,lg_orbits
	
def deinduce(labeling,induced_map,edgelabels):
	edges = tuple([e for e,L in induced_map.items() if L in edgelabels])
	names = tuple(sorted(set(merge_lists([x.nodes() for x in edges]))))
	attrs = tuple(sorted([x for x in labeling.attrs if x.node in names]))
	classes = tuple([labeling.classes[labeling.names.index(x)] for x in names])
	g = CanonicalForm(names,classes,attrs,edges).build_graph_container()
	return g

def kernighan_lin(nodes,edges,orbits):
	# nodes is a list of names
	# edges is a Counter with pairs of nodes as keys
	# orbits is a partition of nodes

	# Algorithm.
	# Start with an initial bi-partition of nodes
	# Keep track of swappable node pairs
	# Greedily choose the best swap in the current available ones
	#	K/L only count crossover edges as cut cost
	#	Here, we also examine if the cut is symmetrically balanced w.r.t. node orbits
	# Fix the swap, eliminate other swapping choices involving the fixed nodes

	partition = split_iter(nodes,2)
	allowed_swaps = list(product(*partition))
	cost = evaluate_cut(partition,edges,orbits)

	while allowed_swaps:
		candidates = [implement_swap(partition,swap) for swap in allowed_swaps]
		costs = [evaluate_cut(p,edges,orbits) for p in candidates]
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

def evaluate_cut(partition,edge_wt,orbits):
	# Cut cost has two costs
	# Typical edgecut counting crossovers
	# Orbcut counting how balanced the orbits are
	edgecut = evaluate_edgecut(partition,edge_wt)
	if len(orbits) == 0:
		return edgecut
	orbcut = evaluate_orbcut(partition,orbits)
	return (edgecut,orbcut)

def evaluate_edgecut(partition,edge_wt):
	# sum weights of crossover edges
	edgecut = 0
	for e in product(*partition):
		edgecut += edge_wt[tuple(sorted(e))]
	return edgecut

def evaluate_orbcut(partition,orbits):
	# for each nontrivial orbit
	# calculate difference in membership between left and right of partition
	# sum over all orbits
	orbcut = 0
	for orb in orbits:
		left,right = [set(orb).intersection(set(x)) for x in partition]
		orbcut += abs(len(right)-len(left))
	return orbcut