from wc_rules.attributes import *
from wc_rules.entity import Entity
from wc_rules.pattern2 import Pattern, GraphContainer
from wc_rules.canonical import canonical_ordering
import random
import unittest

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

def format_p(p):
	# partition- a list of lists of ids
	return [''.join(x) for x in p]

def format_L(L):
	# leader - a dict of id:[ids]
	return ['{x}:{y}'.format(x=x,y=''.join(y)) for x,y in sorted(L.items())]

class TestPattern(unittest.TestCase):

	def test_spoke(self):
		x = X('a')
		x.y = [Y(z) for z in random.sample('bcdef',5)]
		
		g = GraphContainer(x.get_connected())
		p,L = canonical_ordering(g)

		self.assertEqual(format_p(p),['bcdef','a'])
		self.assertEqual(format_L(L),['b:cdef','c:def','d:ef','e:f'])

	def test_directed_wheel(self):
		k = [K(x) for x in 'abcde']
		for i in range(-1,len(k)-1):
			k[i].x = k[i+1]
		
		g = GraphContainer(k[0].get_connected())
		p,L = canonical_ordering(g)
		
		self.assertEqual(format_p(p),['aebdc'])
		self.assertEqual(format_L(L),['a:bcde'])

	def test_undirected_wheel(self):
		m = [M(x) for x in 'abcde']
		for i in range(-1,len(m)-1):
			m[i].x.add(m[i+1])
		
		g = GraphContainer(m[0].get_connected())
		p,L = canonical_ordering(g)
		
		self.assertEqual(format_p(p),['abecd'])
		self.assertEqual(format_L(L),['a:bcde','b:e'])

	def test_directed_cube(self):
		n = [N(x) for x in 'abcdefgh']

		n[0].x = [n[1], n[2], n[3]]
		n[4].x = [n[1], n[2]]
		n[5].x = [n[1], n[3]]
		n[6].x = [n[2], n[3]]
		n[7].x = [n[6], n[5], n[4]]
				
		g = GraphContainer(n[0].get_connected())
		p,L = canonical_ordering(g)

		self.assertEqual(format_p(p),['h','a','efg','bcd'])
		self.assertEqual(format_L(L),['e:fg','f:g'])


	def test_undirected_cube(self):
		m = [M(x) for x in 'abcdefgh']

		m[0].x = [m[1], m[2], m[3]]
		m[4].x = [m[1], m[2]]
		m[5].x = [m[1], m[3]]
		m[6].x = [m[2], m[3]]
		m[7].x = [m[6], m[5], m[4]]

		g = GraphContainer(m[0].get_connected())
		p,L = canonical_ordering(g)

		self.assertEqual(format_p(p),['abcdefgh'])
		self.assertEqual(format_L(L),['a:bcdefgh','b:cd','c:d'])

