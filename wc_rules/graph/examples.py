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

def spoke():
	x = X('a')
	x.y = [Y(z) for z in random.sample('bcdef',len('bcdef'))]
	seed_node,nsyms = x, math.factorial(len('bcdef'))

	g = GraphContainer(seed_node.get_connected())
	return g,nsyms

def directed_wheel():
	#edges: a->b->c->d->e->a
	k = [K(x) for x in 'pqrst']
	for i in range(-1,len(k)-1):
		k[i].x = k[i+1]
	seed_node,nsyms = k[0], len('pqrst')
	g = GraphContainer(seed_node.get_connected())
	return g,nsyms