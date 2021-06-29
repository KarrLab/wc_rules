from ..schema.attributes import *
from ..schema.entity import Entity
from .collections import GraphContainer
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


def single_node():
	x = X('x')
	seed_node, nsyms = x, 1
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
	x.y = [Y(z) for z in random.sample('bcdef',len('bcdef'))]
	seed_node,nsyms = x, math.factorial(len('bcdef'))

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


def gen_all_graphs():

	graphs = [
		single_node,
		spoke,
		directed_square,
		directed_wheel,
		undirected_wheel,
		directed_cube,
		undirected_cube,
		clique
		]
	return {g.__name__:g() for g in graphs}
