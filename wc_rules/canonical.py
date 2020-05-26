from functools import reduce
from collections import defaultdict,deque
from pprint import pformat
from copy import deepcopy

def canonize(g):

	partition = compute_initial_partition(g)
	if len(partition)!=len(g):
		new_partition = deque()
		old_length = len(partition)
		while partition:
			cell = partition.popleft()
			celldeque = partition_current_cell(new_partition,cell,g)
			print(new_partition,celldeque,partition)
			if len(celldeque)==1:
				new_partition += celldeque
			else:
				partition += celldeque
			if len(partition)==0 and len(new_partition) > old_length:
				partition = new_partition
				old_length=len(partition)
				new_partition = deque()
			print(partition)		
		partition = new_partition
	print(partition)
	return True

def partition_current_cell(partition,cell,g):
	# if cell is compatible and doesn't need to be subdivided,
	# return deque([cell])
	# else: partition into smaller cells and return deque([cell1,cell2,cell3])
	if len(cell)==1:
		return deque([cell])

	indexes = index_partition(partition+deque([cell]))
	certs = defaultdict(list)
	for node in cell:
		sgn = get_neighbor_signature(node,indexes,g)
		certs[ sgn ].append(node)
	
	cells = [certs[sgn] for sgn in sorted(certs)]
	return deque(cells)

def get_neighbor_signature(node,indexes,g):
	neighbors = []
	for attr in g[node].get_nonempty_related_attributes():
		for neighbor in g[node].listget(attr):
			if neighbor.id in indexes:
				neighbors.append((attr,indexes[neighbor.id]))
	return tuple(sorted(neighbors))

def index_partition(partition):
	indexes = dict()
	for i,cell in enumerate(partition):
		for node in cell:
			indexes[node] = i
	return indexes	



def compute_initial_partition(g):
	# create a signature for each node
	# (degree,class_name,sorted_edge_tuples)
	# .... sorted_edge_tuples = (attr,destination_class), (attr,destination_class), ...
	# collect nodes with same signature
	eqv = defaultdict(list)
	for node in g:
		edges = [(attr,x.__class__.__name__) for attr in node.get_nonempty_related_attributes() for x in node.listget(attr)]
		edges = tuple(sorted(edges))
		sgn = (len(edges),node.__class__.__name__,edges) 
		eqv[ sgn ].append(node.id)
	return deque([ sorted(eqv[sgn]) for sgn in sorted(eqv) ])



def invert_map(d):
	# {v:[k1,k2..] for k:v}
	out = dict({v:[] for v in set(d.values())})
	for k,v in d.items():
		out[v].append(k)
	return dict(out)

def invert_bmap(d):
	# {v:k for k:v} use carefully
	return {v:k for k,v in b.items()}