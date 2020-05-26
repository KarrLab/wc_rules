from functools import reduce
from pprint import pformat

def canonize(g):
	# g is a scaffold
	equivalence_classes = compute_equivalence_classes(g)
	print(pformat(equivalence_classes))
	return True

def sequentiate_dicts(*dicts,keys=None):
	# for dicts d1,d2,d3... returns a dict such that
	# out[key] = d3[d2[d1[key]]]
	if keys is None:
		keys= dicts[0].keys()
	return {key:reduce(lambda key,d: d[key],dicts,key) for key in keys}

def renumber_by_value(d):
	# indexes unique elements from d.values,
	# then, replaces values in d by index
	# e.g. dict(x='a',y='a',z='b') --> dict(x=0,y=0,z=1)
	v = {x:i for i,x in enumerate(sorted(set(d.values())))}
	return sequentiate_dicts(d,v)

def compute_equivalence_classes(g):
	# this is the initial step of sorting nodes
	# in some initial set of equivalence classes
	eqv = dict()
	for node in g:
		eqv[node.id] = compute_signature(node)
	return renumber_by_value(eqv)

def compute_signature(node):
	# signature determines the initial sorting of nodes
	# the current signature is degree,classname,sorted_individual_edges
	_cls = node.__class__.__name__
	edges = []
	for attr in node.get_related_attributes():
		edges.extend([(attr,x.__class__.__name__) for x in node.listget(attr)])

	edges = tuple(sorted(edges))
	signature = (len(edges),_cls,edges)
	return signature
	