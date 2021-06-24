from wc_rules.schema.attributes import *
from wc_rules.schema.entity import Entity
from wc_rules.graph.collections import GraphContainer
from wc_rules.graph.canonical import canonical_ordering, compute_symmetries, compute_symmetry_generators
from wc_rules.graph.canonical_labeling import canonical_label
import wc_rules.graph.examples as gex

from dataclasses import dataclass
from typing import Any

import math
import random
from collections import defaultdict

import unittest
from parameterized import parameterized

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
	d = defaultdict(list)
	for x,y in L:
		d[x].append(y)
	# leader - a dict of id:[ids]
	return ['{x}:{y}'.format(x=x,y=''.join(y)) for x,y in sorted(d.items())]

def do_computations(seed_node):
	g = GraphContainer(seed_node.get_connected())
	p,order,L = canonical_ordering(g)
	generators = compute_symmetry_generators(g,p,order)
	syms = compute_symmetries(generators)
	return p,L,syms

@dataclass(frozen=True,eq=True)
class CanonicalLabelBuild:
	mapping: Any
	labeling: Any
	group: Any

class TestCanonicalLabel(unittest.TestCase):
	@parameterized.expand([
		("single_node",*gex.single_node()),
		("spoke",*gex.spoke()),
		("directed_wheel",*gex.directed_wheel())
	])
	def test_graph(self,name,g,nsyms):
		build0 = CanonicalLabelBuild(*canonical_label(g))

		# reconstruct g as g1 using build0.mapping
		# prove g1==g, i.e. build(g1) == build(g)
		g1 = build0.labeling.build_graph_container(build0.mapping)
		build1 = CanonicalLabelBuild(*canonical_label(g1))
		self.assertEqual(build0.mapping,build1.mapping)
		self.assertEqual(build0.labeling,build1.labeling)

		# construct a canonical graph g2 equivalent to g
		# build(g2) should have identity mapping,
		# but same canonical form
		g2 = build0.labeling.build_graph_container()
		build2 = CanonicalLabelBuild(*canonical_label(g2))
		self.assertEqual(build2.mapping.sources, build2.mapping.targets)
		self.assertEqual(build0.labeling,build2.labeling)

		# permutation group relations
		# build0 and build1 must have an identical permgroup
		# since they are built from the same graph
		self.assertEqual(build0.group,build1.group)

		# build0.group and build2.group must be equivalent in expansion
		# but are not guaranteed to have the same generator-form
		p0,p2 = [x.group.expand() for x in [build0,build2]]
		self.assertEqual(p0,p2)

		# the expanded-form must have the expected number of permutations
		self.assertEqual(len(p0),nsyms)
		

class TestGraph2(unittest.TestCase):

	def test_single_node(self):
		seed_node = X('x')
		p,L,syms = do_computations(seed_node)
		self.assertEqual(format_p(p),['x'])
		self.assertEqual(format_L(L),[])
		self.assertEqual(len(syms),1)

	def test_spoke(self):
		#edges: a-b, a-c, a-d, a-e, a-f
		x = X('a')
		x.y = [Y(z) for z in random.sample('bcdef',len('bcdef'))]

		seed_node= x
		p,L,syms = do_computations(seed_node)
		
		self.assertEqual(format_p(p),['a','bcdef'])
		self.assertEqual(format_L(L),['b:cdef','c:def','d:ef','e:f'])
		self.assertEqual(len(syms),math.factorial(len('bcdef')))

	def test_directed_wheel(self):
		#edges: a->b->c->d->e->a
		k = [K(x) for x in 'abcde']
		for i in range(-1,len(k)-1):
			k[i].x = k[i+1]
		
		seed_node = k[0]
		p,L,syms = do_computations(seed_node)
		
		self.assertEqual(format_p(p),['aebdc'])
		self.assertEqual(format_L(L),['a:bcde'])
		self.assertEqual(len(syms),len('abcde'))

	def test_undirected_wheel(self):
		#edges: a-b-c-d-e-a
		m = [M(x) for x in 'abcde']
		for i in range(-1,len(m)-1):
			m[i].x.add(m[i+1])
		
		seed_node = m[0]
		p,L,syms = do_computations(seed_node)

		self.assertEqual(format_p(p),['abecd'])
		self.assertEqual(format_L(L),['a:bcde','b:e'])
		self.assertEqual(len(syms),2*len('abcde'))

	def test_directed_cube(self):
		#edges: a->[b,c,d], [b,c]->e, [b,d]->f, [c,d]->g, [e,f,g]->h
		n = [N(x) for x in 'abcdefgh']

		n[0].x = [n[1], n[2], n[3]]
		n[4].x = [n[1], n[2]]
		n[5].x = [n[1], n[3]]
		n[6].x = [n[2], n[3]]
		n[7].x = [n[6], n[5], n[4]]
				
		seed_node = n[0]
		p,L,syms = do_computations(seed_node)

		self.assertEqual(format_p(p),['h','a','efg','bcd'])
		self.assertEqual(format_L(L),['e:fg','f:g'])
		self.assertEqual(len(syms),6)


	def test_undirected_cube(self):
		#edges: a-[b,c,d], [b,c]-e, [b,d]-f, [c,d]-g, [e,f,g]-h
		m = [M(x) for x in 'abcdefgh']

		m[0].x = [m[1], m[2], m[3]]
		m[4].x = [m[1], m[2]]
		m[5].x = [m[1], m[3]]
		m[6].x = [m[2], m[3]]
		m[7].x = [m[6], m[5], m[4]]

		seed_node = m[0]
		p,L,syms = do_computations(seed_node)

		self.assertEqual(format_p(p),['abcdefgh'])
		self.assertEqual(format_L(L),['a:bcdefgh','b:cd','c:d'])
		self.assertEqual(len(syms),48)

	def test_clique(self):
		#edges: a-[b,c,d,e], b-[c,d,e], c-[d,e], d-e
		m = [M(x) for x in 'abcde']
		for i in range(len(m)):
			for j in range(i+1,len(m)):
				m[i].x.add(m[j])

		seed_node = m[0]
		p,L,syms = do_computations(seed_node)

		self.assertEqual(format_p(p),['abcde'])
		self.assertEqual(format_L(L),['a:bcde','b:cde','c:de','d:e'])
		self.assertEqual(len(syms),math.factorial(len('abcde')))