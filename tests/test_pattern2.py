from wc_rules.chem import *
from wc_rules.attributes import *
from wc_rules.pattern import Pattern
import unittest

class M1(Molecule):
	sources = ManyToManyAttribute('M1',related_name='sources')

class M2(Molecule):
	sources = ManyToManyAttribute('M2',related_name='targets')


class A(Molecule):pass
class X(Site):
    x = BooleanAttribute()
    y = IntegerAttribute()

class TestPattern(unittest.TestCase):

	def test_symmetry_00(self):
		# no symmetry
		a = A('a')
		x = X('x')
		a.sites.add(x)

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),1)
		self.assertTrue(len(p1._final_orbits),2)
		
	def test_symmetry_01(self):

		# symmetry of x1<-attr,attr->x2
		a = M1('a')
		b = M1('b')
		a.sources.add(b)

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),2)
		self.assertTrue(len(p1._final_orbits),1)
		self.assertTrue(p1._final_orbits.pop(),frozenset({'a','b'}))

		# same thing x1,x2,x3
		a = M1('a')
		b = M1('b')
		c = M1('c')
		a.sources.add(b)
		a.sources.add(c)
		b.sources.add(c)

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),3)
		self.assertTrue(len(p1._final_orbits),1)
		self.assertTrue(p1._final_orbits.pop(),frozenset({'a','b','c'}))

	def test_symmetry_02(self):
		# symmetry of x1<-attr1,attr2->x2<-attr1,attr2->x1
		a = M2('a')
		b = M2('b')

		a.sources.add(b)
		a.targets.add(b)	

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),2)
		self.assertTrue(len(p1._final_orbits),1)
		self.assertTrue(p1._final_orbits.pop(),frozenset({'a','b'}))	

		# same thing x1,x2,x3
		a = M2('a')
		b = M2('b')
		c = M2('c')
		a.sources.add(b)
		a.sources.add(c)
		b.sources.add(c)

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),1)
		self.assertTrue(len(p1._final_orbits),3)

		a.targets.add(b)
		a.targets.add(c)
		b.targets.add(c)

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),3)
		self.assertTrue(len(p1._final_orbits),1)
		self.assertTrue(p1._final_orbits.pop(),frozenset({'a','b','c'}))

	def test_symmetry_03(self):
		# simple site-bond
		a = Site('site')
		bnd = Bond('bond').add_sites(a)

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),1)
		self.assertTrue(len(p1._final_orbits),2)

		# simple site-bond-site
		a = Site('site')
		b = Site('partner')
		bnd = Bond('bond').add_sites(a,b)

		p1 = Pattern('p1').add_node(a)
		p1.finalize()

		self.assertTrue(len(p1._final_symmetries),2)
		self.assertTrue(len(p1._final_orbits),2)
