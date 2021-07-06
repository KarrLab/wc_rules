from pathlib import Path
import jinja2

def visualize_graph_container(g,asdict=True):
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
	if asdict:
		return dict(nodes=nodes,edges=edges)
	else:
		template = load_template('template_graphcontainer.html')
		return template.render(graph=dict(nodes=nodes,edges=edges))
	assert False

def visualize_graph_partitioning(graphs):
	# each g is a graph container
	# assume every three elements is a partition tuple: parent,child,child
	graphs = [visualize_graph_container(g) for g in graphs]
	template = load_template('template_partitioning.html')
	return template.render(graphs=graphs)

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

