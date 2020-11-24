from wc_rules.entity import Entity
from wc_rules.attributes import IntegerAttribute, OneToOneAttribute
from wc_rules.constraint import Constraint
from wc_rules.actions import parser

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

	def test_action_grammar(self):
		t1 = "p.a.add_molecule(q.b)"
		t2 = "p.a.set_phospho(True)"
		t21 = "p.a.set_nloops(5)"
		t3 = "p.a.add_molecule(v)"
		t4 = "p_x.a.add_sites(q.b,r.c)"
		t5 = "p.a.set_phospho(q.contains(x=z))"
		t6 = "p.a.remove_molecule(q.b)"
		t7 = "p.a.remove()"
		t8 = "p.remove()"

		for s in [t1]:
			t = parser.parse(s)
			self.assertEqual(t.data,'graph_action')

		t5 = "p.a_x.addMove(by=5)"
		t = parser.parse(t5)
		self.assertEqual(t.data,'custom_action')

		s1 = "12345"
		s2 = "True"
		s3 = "all(a.x,b.y,c.z)"
		s4 = "p.contains(x=z)==True"
		s5 = "a.x + b.y <= c.z"
		
		
		for s in [s1,s2,s3,s4,s5]:
			t = parser.parse(s)
			self.assertEqual(t.data,'expression')

		### NOTABLE FAILURE and RESULTANT AMBIGUITY
		### To resolve set complicated expressions as v=expr
		### then use v as v==True or p.a.action(v)

		# s6 = "p.a.compute(x=y,p=q) != all(a.x,p.contains(x=z))"
		# u1 = "p.a.set_ph({0})".format(s6) 
		# In both cases, the parser is matching "q) != all(..."
		# as an expression
		# in s6, it incorrectly tries to parse as action
		# in u1, it incorrectly tries to parse as expression
		