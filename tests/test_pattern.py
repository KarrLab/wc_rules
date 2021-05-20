
from wc_rules.schema.attributes import *
from wc_rules.schema.entity import Entity
from wc_rules.graph.collections import GraphContainer
from wc_rules.modeling.pattern import Pattern
from wc_rules.expressions.executable import Constraint
import math

import unittest

class X(Entity): 
	i = IntegerAttribute()
	j = IntegerAttribute()
	k = IntegerAttribute()

class Y(Entity):
	x = ManyToOneAttribute(X,related_name='y')

class Z(Entity):
	a = BooleanAttribute()
	b = BooleanAttribute()
	z = OneToOneAttribute('Z',related_name='z')

class K(Entity):
	x = OneToOneAttribute('K',related_name='y')

class TestPattern(unittest.TestCase):

	def test_graphcontainer(self):
		with self.assertRaises(AssertionError):
			x = X('x',y=[Y('y1'),Y('y1')])
			GraphContainer(x.get_connected())

		x = X('x',y=[Y('y1'),Y('y2')])
		g = GraphContainer(x.get_connected())
		self.assertEqual([g[elem].__class__ for elem in ['x','y1','y2']], [X,Y,Y])
		g.validate_connected()

		with self.assertRaises(AssertionError):
			g = GraphContainer([X('x'),Y('y1'),Y('y2')])
			g.validate_connected()
			
	def test_pattern_build(self):

		with self.assertRaises(AssertionError):
			x = object()
			px = Pattern(x)
		
		x = X('x',y=[Y('y1'),Y('y2')])
		px = Pattern(parent=GraphContainer(x.get_connected()))
		self.assertEqual(px.namespace, dict(x=X,y1=Y,y2=Y))

		pxx = Pattern(parent=px)
		self.assertEqual(pxx.namespace, dict(x=X,y1=Y,y2=Y))
		del px,pxx
		

		px = Pattern(parent=GraphContainer([X('x',i=10)]))
		# self.assertEqual(px.namespace, dict(x=X,_0='x.i == 10'))

		pxx = Pattern(px, helpers={'px':px}, constraints=['px.contains(x=x)==True'])
		#self.assertEqual(pxx.namespace, dict(x=X,px=px,_0='x.i == 10',_1='px.contains(x=x) == True'))
		del pxx

		with self.assertRaises(AssertionError):
			pxx = Pattern(parent=px, helpers={'px':px}, constraints='px=5')

		with self.assertRaises(AssertionError):
			pxx = Pattern(parent=px, helpers={'px':px}, constraints='t==5')

	def test_boolean_constraints(self):
		z = Z('z1',z=Z('z2'))
		pz = Pattern(
			parent = GraphContainer(z.get_connected()), 
			constraints = [
				'any(z1.a,z1.b,z2.a,z2.b) == True',
				'inv(any(z1.a,z1.b,z2.a,z2.b)) == False',
				'all(z1.a,z1.b,z2.a,z2.b) == True',
				'only_one_true(z1.a,z1.b,z2.a,z2.b) == True',
				'only_one_false(z1.a,z1.b,z2.a,z2.b) == True',
			])
		
		matches = [
		dict(z1=Z(a=False,b=False), z2=Z(a=False,b=False)),
		dict(z1=Z(a=False,b=False), z2=Z(a=False,b=True)),
		dict(z1=Z(a=True,b=True), z2=Z(a=True,b=False)),
		dict(z1=Z(a=True,b=True), z2=Z(a=True,b=True)),
		]

		expected_values = [
		[False, True, True, True ],
		[False, True, True, True ],
		[False, False, False, True ],
		[False, True, False, False ],
		[False, False, True, False ],
		]


		computed_values = [[c.exec(match) for match in matches] for c in pz.make_executable_constraints()]

		self.assertEqual(computed_values,expected_values)

	def test_list_constraints(self):		
		px = Pattern(
			parent = GraphContainer([X('x')]),
			constraints = [
			'max(x.i,x.j,x.k) == 30',
			'min(x.i,x.j,x.k) == 10',
    		'sum(x.i,x.j,x.k) == 60',
    		'len(x.y) == 2',
    		])

		match = dict(x = X(y=[Y(),Y()],i=10,j=20,k=30))
		execs = px.make_executable_constraints()
		for c in execs:
			self.assertTrue(c.exec(match,{}))

		pz = Pattern(parent=GraphContainer([Z('z')]),constraints=['len(z.z) > 0'])
		c = pz.make_executable_constraints()[0]
		self.assertEqual(c.exec(dict( z=Z() )), False)
		self.assertEqual(c.exec(dict( z=Z(z=Z()) )), True)

	@unittest.skip("Upgrade to new patterns")
	def test_canonical_expr(self):
		z = Z('z1',z=Z('z2'))
		pz = Pattern(parent=GraphContainer(z.get_connected()))

		cP, cL = (('z1','z2'),), (('z1','z2'),)
		self.assertEqual(pz.partition,cP)
		self.assertEqual(pz.leaders,cL)

		# symmetry preserving
		pzz = Pattern(
			parent = pz,
			constraints = [
			'a = any(z1.a,z2.a)',
			'b = all(z1.b,z2.b)',
			'c = any(z1.a,z1.b)',
			'd = any(z2.a,z2.b)',
			'any(a,b,c,d) == True',
			])

		self.assertEqual(pzz.partition,cP)
		self.assertEqual(pzz.leaders,cL)

		# symmetry breaking
		cP, cL = (('z1',),('z2',),), tuple()
		pzzz = Pattern(pz,constraints=['a = any(z1.a,z1.b,z2.a)'])

		self.assertEqual(pzzz.partition,cP)
		self.assertEqual(pzzz.leaders,cL)


		# symmetry preserving + using helpers
		z = Z('z',a=True,b=False)
		pz = Pattern(parent=GraphContainer([z]))

		zz = Z('z1',z=Z('z2'))
		pzz = Pattern(parent=GraphContainer(zz.get_connected()),
			helpers = {'pz':pz},
			constraints = 'pz.contains(z=z1)==True \n pz.contains(z=z2)==True',
			)
		cP, cL = (('z1','z2'),), (('z1','z2'),)
		self.assertEqual(pzz.partition,cP)
		self.assertEqual(pzz.leaders,cL)

		# symmetry breaking + using helpers
		pzz = Pattern(parent=GraphContainer(zz.get_connected()),
			helpers = {'pz':pz},
			constraints = 'pz.contains(z=z1)==True',
			)
		cP, cL = (('z2',),('z1',),), tuple()
		self.assertEqual(pzz.partition,cP)
		self.assertEqual(pzz.leaders,cL)