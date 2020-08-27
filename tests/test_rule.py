from wc_rules.entity import Entity
from wc_rules.attributes import IntegerAttribute, OneToOneAttribute
from wc_rules.constraint import Constraint

import math
import unittest

class A(Entity):
	x = IntegerAttribute()
	y = IntegerAttribute()

class P(Entity):
	a = OneToOneAttribute(A,related_name='p')
	b = OneToOneAttribute(A,related_name='q')


class TestRule(unittest.TestCase):
	
	def test_constraint_objects(self):
		# constraint objects are used by both patterns and rules
		# constraints of the form p.a.x are disallowed in patterns, but allowed in rules
		# this test is to check whether constraint objects support both behaviors
		a,b,p,q = A(x=1), A(y=2), P(), P()
		p.a, q.b = a,b

		s = "v = a.x + b.y"
		c,var = Constraint.initialize(s)
		self.assertEqual([var,c.code,sorted(c.keywords)],['v','a.x + b.y',['a','b']])
		match = {'a':a,'b':b}
		self.assertEqual(c.exec(match),3)

		s = "v = p.a.x + q.b.y"
		with self.assertRaises(ValueError):
			c,var = Constraint.initialize(s)

		c,var = Constraint.initialize(s,has_subvariables=True)
		self.assertEqual([var,c.code],['v','p.a.x + q.b.y'])
		match = {'p':p,'q':q}
		self.assertEqual(c.exec(match),3)

