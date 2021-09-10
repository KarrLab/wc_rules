from pathlib import Path
import jinja2
from ..expressions.exprgraph_utils import ExprBase

def visualize_graph_container(g,asdict=False):
	nodes,edges = [],[]
	for idx,node in g.iter_nodes():
		classname = node.__class__.__name__
		size = 20
		font = {'size':20,'face':'arial'}
		nodes.append(dict(id=idx,label=idx,size=size,group=classname,title=classname,font=font))
		
	for edge in g.iter_edges():
		arrows = dict()
		n1,a1,n2,a2 = edge.unpack()
		if a1 < a2:
			arrows.update({'to':{'enabled':True,'type':'arrow'}})
		if a1 > a2:
			arrows.update({'from':{'enabled':True,'type':'arrow'}})
		_from, _to = n1,n2
		edges.append({'from':_from,'to':_to,'title':edge.pprint(),'arrows':arrows})
	d = dict(nodes=nodes,edges=edges)
	
	if asdict:
		return d
	
	template = load_template('template_graphcontainer.html')
	return template.render(graph=d)
	
def visualize_graph_partitioning(graphs):
	# each g is a graph container
	# assume every three elements is a partition tuple: parent,child,child
	graphs = [visualize_graph_container(g,asdict=True) for g in graphs]
	template = load_template('template_partitioning.html')
	return template.render(graphs=graphs)

def visualize_node(node,idx,label,size=20,font={'size':20,'face':'arial'}):
	classname = node.__class__.__name__
	return dict(id=idx,label=label,size=size,group=classname,title=classname,font=font)

def visualize_exprgraph(g,asdict=False):
	nodes,edges = [],[]
	for idx,node in g.iter_nodes():
		label = node.serialize_for_vis() if isinstance(node,ExprBase) else node.id
		nodes.append(visualize_node(node=node,idx=node.id,label=label))
		
	for edge in g.iter_edges():
		arrows = dict()
		n1,a1,n2,a2 = edge.unpack()
		if a1 < a2:
			arrows.update({'to':{'enabled':True,'type':'arrow'}})
		if a1 > a2:
			arrows.update({'from':{'enabled':True,'type':'arrow'}})
		_from, _to = n1,n2
		edges.append({'from':_from,'to':_to,'title':edge.pprint(),'arrows':arrows})
	d = dict(nodes=nodes,edges=edges)
	
	if asdict:
		return d
	
	template = load_template('template_exprgraph.html')
	return template.render(graph=d)

# loading Jinja template
def load_template(name):
	p = Path(__file__).parent / 'templates'
	env = jinja2.Environment(loader=jinja2.FileSystemLoader(p))
	template = env.get_template(name)
	return template

class VisUtil:

	def __init__(self,folder='.'):
		self.folder = Path(folder)

	def write(self,name,txt):
		filename = f'{name}.html'
		file = self.folder / filename
		self.folder.mkdir(parents=True,exist_ok=True)
		file.write_text(txt)
		return

