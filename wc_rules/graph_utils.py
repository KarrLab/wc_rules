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
	
def get_edges(node):
	edges = []
	for attrname in node.__class__.GraphMeta.outward_edges:
		if getattr(node,attrname) is not None:
			attr_obj = getattr(node,attrname)
			if isinstance(attr_obj,core.RelatedManager):
				for x in attr_obj:
					edges.append(tuple([node,x]))
					edges.extend(x.get_edges())
			else:
				edges.append(tuple([node,attr_obj]))
	return edges

def get_graph(node):
	return nx.DiGraph(node.get_edges())