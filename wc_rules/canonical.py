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
		return [self[key] for key in sorted(self)]



def canonize(g):
	partition = canonical_partition(g)
	labels = [x for cell in partition for x in cell]
	relabeling =  generate_relabeling(labels)
	new_partition = [[relabeling[x] for x in cell] for cell in partition]
	return (new_partition,relabeling)


####### methods for generating a canonical label from a canonical partition
def generate_relabeling(_list):
	n = len(_list)
	relabels = list(map(lambda x:''.join(x),list(product('abcdefgh',repeat = math.ceil(n/8)))[0:n]))
	return dict(zip(_list,relabels))


####### methods for generating a canonical partition of a scaffold graph
def canonical_partition(g):
	rhs, lhs, modified = initial_partition(g), deque(), False
	indexes = index_partition(rhs)
	while rhs:
		prev_length = len(lhs)
		lhs += partition_cell(rhs.popleft(),indexes,g)
		if len(lhs) > prev_length+1:
			indexes, modified  = index_partition(lhs+rhs), True
		if len(rhs)==0 and modified:
			rhs, lhs, modified = lhs, deque(), False
	return lhs

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

