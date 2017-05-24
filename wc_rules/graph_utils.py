from obj_model import core
import networkx as nx

class GraphMeta(core.Model.Meta):
	""" Inner class holding values used in graph methods
	Attributes:
	* outward_edges (:obj:`str`): attributes to be examined recursively for get_edges(). 
	Only RelatedManager attributes allowed.
	* semantic (:obj:`str`): attributes/properties should be examined for node_match(). 
	Only attributes/properties that return values comparable by '==' allowed.	
	"""
	outward_edges = tuple()
	semantic = tuple()

def node_match(node1,node2):
	#### this is to be compatible with networkx's subgraph isomorphism algorithm
	# node2 is from the smaller graph
	# node1 is from the bigger graph
	return node2.node_match(node1)

def node_compare(current,other):
	#### Logic: can current node's semantic properties be entirely contained within other node?
	# current --- None returns False
	# current --- other returns False if 
	# 	other is not an instance of type(current) or any subclass thereof
	# current --- other returns False if	
	# 	attributes in 'semantic' list (see GraphMeta class) do not match in value, i.e.
	#		None --- anything is a match
	#		current.attrib --- None is not a match
	#		current.attrib == current.attrib is a match
	if other is None: return False
	if isinstance(other,(current.__class__,)) is not True:
		return False
	for attrname in current.__class__.GraphMeta.semantic:
		current_attr = getattr(current,attrname)
		other_attr = getattr(other,attrname)
		if current_attr is not None:
			if other_attr is None: return False
		if current_attr != other_attr: return False
	return True
	
def get_graph(current_obj,recurse=True,memo=None):
	def update_graph(graph,obj1):
		if id(obj1) not in graph:
			graph.add_node(id(obj1),obj=obj1)
		else:
			graph.node[id(obj1)]['obj'] = obj1

	# Initializing if a memo is not provided
	if memo is None:
		memo = nx.DiGraph()
	# Adding node if not already in memo, else updating it
	update_graph(memo,current_obj)
	
	# getting list of next nodes to check
	next_nodes = []
	for attrname in current_obj.__class__.GraphMeta.outward_edges:
		if getattr(current_obj,attrname) is not None:
			attr = getattr(current_obj,attrname)
			if isinstance(attr,list):
				next_nodes.extend(attr)
			else:
				next_nodes.append(attr)
	# for each node in next_nodes,
	# if an edge already exists, ignore
	# if adding a new edge, recurse onto that node using current memo
	for x in next_nodes:
		update_graph(memo,x)
		e = tuple([id(current_obj),id(x)])
		if e not in memo.edges():
			memo.add_edge(*e)
			if recurse is True:
				memo2 = x.get_graph(recurse=True,memo=memo)
				memo = memo2
	return memo