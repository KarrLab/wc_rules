from pathlib import Path
import networkx as nx
from pyvis.network import Network

def visualize_graph_container(g):
	# g is a GraphContainer
	nxg = nx.DiGraph()
	size = 20
	for idx,node in g.iter_nodes():
		classname = node.__class__.__name__
		nxg.add_node(idx,
			size=size,
			group=classname,
			title=classname,
			)
	# edge size
	value = 5
	for edge in g.iter_edges():
		arrows = dict()
		n1,a1,n2,a2 = edge.unpack()
		if a1 < a2:
			arrows.update({'to':{'enabled':True,'type':'arrow'}})
		if a1 > a2:
			arrows.update({'from':{'enabled':True,'type':'arrow'}})
		nxg.add_edge(*edge.nodes(), 
			title=edge.pprint(),
			arrows=arrows
			)
	return nxg

class VisUtil:

	converters = {
		'GraphContainer': visualize_graph_container
	}

	def __init__(self,folder='.'):
		self.folder = Path(folder)
		self.network_args = ['500px','500px']

	def write(self,x,name,converter=None):
		if converter is None:
			converter = self.converters[x.__class__.__name__]
		filename = f'{name}.html'
		path = self.folder / filename
		self.folder.mkdir(parents=True,exist_ok=True)
		nx_graph = converter(x)
		nt = Network(*self.network_args)
		nt.from_nx(nx_graph)
		nt.show(str(path))
		return

