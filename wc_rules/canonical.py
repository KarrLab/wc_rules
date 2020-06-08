from functools import partial
from itertools import product
from collections import defaultdict,deque
from pprint import pformat
import math

class CertificateCounter(defaultdict):
	def __init__(self,fn,_list):
		# applies fn to each element of _list to create a certificate
		# then collects groups with the same certificate
		# maintains sorting order of _list
		super().__init__(list)
		for elem in _list:
			self[fn(elem)].append(elem)

	def groups(self):
		# returns groups in sorted order of certificates
		#print([[key,self[key]] for key in sorted(self)])
		return [self[key] for key in sorted(self)]



####### methods for generating a canonical partition of a graph container
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


def canonical_ordering(g):
	# initially partition based on node classes and degrees
	# then refine until valid
	partition = refine_partition(g,initial_partition(g))
	# now cells == orbits, but individual orbits need to be ordered

	p, leaders = partition.copy(), dict()
	# until all orbits broken
	while len(p) < len(g):
		# find first non-trivial orbit
		# separate its lexicographic leader
		# refine until valid
		idx = [i for i,x in enumerate(p) if len(x)>1][0]
		leader, remaining = p[idx][0], p[idx][1:]
		leaders[leader] = remaining
		p[idx:idx+1] = [ [leader], remaining ]  
		p = refine_partition(g,p)

	order = [x for y in p for x in y]

	# use acquired order to sort partition cells
	for x in partition:
		x.sort(key = lambda x: order.index(x))

	return partition,leaders



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


def invert_map(d):
	# assume map is one to one
	return {y:x for x,y in d.items()}

