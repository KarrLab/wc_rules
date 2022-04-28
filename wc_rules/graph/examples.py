from ..schema.attributes import *
from ..schema.entity import Entity
from .collections import GraphContainer
from .canonical_labeling import canonical_label

import random,math

class X(Entity): 
	pass
class Y(Entity):
	x = ManyToOneAttribute(X,related_name='y')

class K(Entity):
	x = OneToOneAttribute('K',related_name='y')

class M(Entity):
	x = ManyToManyAttribute('M',related_name='x')

class N(Entity):
	x = ManyToManyAttribute('N',related_name='y')	

class E(Entity):
	e = OneToOneAttribute('E',related_name='e')

class F(Entity):
	e = OneToManyAttribute(E,related_name='f')
	f = OneToOneAttribute('F',related_name='f_rel')

def single_node():
	x = X('x')
	seed_node, nsyms = x, 1
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms	

def single_edge_asymmetric():
	x = X('x',y=[Y('y')])
	seed_node, nsyms = x, 1
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def two_edges():
	x =  X('x',y=[Y('y1'),Y('y2')])
	seed_node, nsyms = x, 2
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def single_edge_symmetric():
	x = E('e1',e=E('e2'))
	seed_node, nsyms = x, 2
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def directed_square():
	k = [K(x) for x in 'abcd']
	for i in range(-1,len(k)-1):
		k[i].x = k[i+1]
	seed_node,nsyms = k[0], len('abcd')
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def spoke():
	x = X('a')
	x.y = [Y(z) for z in random.sample('bcde',len('bcde'))]
	seed_node,nsyms = x, math.factorial(len('bcde'))

	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def directed_wheel():
	#edges: a->b->c->d->e->a
	k = [K(x) for x in 'abcde']
	for i in range(-1,len(k)-1):
		k[i].x = k[i+1]
	seed_node,nsyms = k[0], len('abcde')
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def undirected_wheel():
	#edges: a-b-c-d-e-a
	m = [M(x) for x in 'abcde']
	for i in range(-1,len(m)-1):
		m[i].x.add(m[i+1])	
	seed_node,nsyms = m[0], 2*len('abcde')
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def directed_cube():
	#edges: a->[b,c,d], [b,c]->e, [b,d]->f, [c,d]->g, [e,f,g]->h
	a,b,c,d,e,f,g,h = [N(x) for x in 'abcdefgh']
	a.x = [b,c,d]
	e.y = [b,c]
	f.y = [b,d]
	g.y = [c,d]
	h.y = [e,f,g]
	seed_node,nsyms = a,3*2

	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def undirected_cube():
	#edges: a-[b,c,d], [b,c]-e, [b,d]-f, [c,d]-g, [e,f,g]-h
	a,b,c,d,e,f,g,h = [M(x) for x in 'abcdefgh']
	a.x = [b,c,d]
	e.x = [b,c]
	f.x = [b,d]
	g.x = [c,d]
	h.x = [e,f,g]

	seed_node,nsyms = a,8*3*2
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def clique():
	m = [M(x) for x in 'abcde']
	for i in range(len(m)):
		for j in range(i+1,len(m)):
			m[i].x.add(m[j])

	seed_node,nsyms = m[0], math.factorial(len('abcde'))
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def bowtie():
	f1,f2 = F('f1'), F('f2')
	e1,e2,e3,e4 = [E('e'+str(i)) for i in range(1,5)]
	f1.e = [e1,e2]
	f2.e = [e3,e4]
	f1.f = f2
	f2.f = f1
	e1.e = e2
	e3.e = e4

	seed_node,nsyms = f1, 8
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms


graphs = [
		single_node,
		single_edge_asymmetric,
		two_edges,
		spoke,
		directed_square,
		directed_wheel,
		undirected_wheel,
		directed_cube,
		undirected_cube,
		clique,
		bowtie
		]

def gen_all_graphs():
	return {g.__name__:g() for g in graphs}

def get_graph(name):
	return [f() for f in graphs if f.__name__==name][0][0]

def get_canonical_label(name):
	mapping, labeling, symmetry_group = canonical_label(get_graph(name))
	return mapping,labeling,symmetry_group