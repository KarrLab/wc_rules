from wc_rules.entity import Entity
from wc_rules.attributes import IntegerAttribute, OneToOneAttribute
from wc_rules.constraint import Constraint, Computation
from wc_rules.rule import RateLaw
#from wc_rules.actions import parser

import math
import unittest

class A(Entity):
	x = IntegerAttribute()
	y = IntegerAttribute()

class P(Entity):
	a = OneToOneAttribute(A,related_name='p')
	b = OneToOneAttribute(A,related_name='q')


class TestRule(unittest.TestCase):
	
	def test_executable_expression_objects(self):
		# constraint objects are used by both patterns and rules
		# constraints of the form p.a.x are disallowed in patterns, but allowed in rules
		# this test is to check whether constraint objects support both behaviors
		a,b,p,q = A(x=1), A(y=2), P(), P()
		p.a, q.b = a,b

		s = "v = a.x + b.y"
		# constraint initializiation should fail
		self.assertEqual(Constraint.initialize(s),None)
		# computation initialization should pass
		x = Computation.initialize(s)
		self.assertTrue(x is not None)
		# check object properties
		self.assertTrue(isinstance(x,Computation))
		self.assertEqual(x.deps.declared_variable,'v')
		self.assertEqual(x.code,'a.x + b.y')
		self.assertEqual(sorted(x.keywords),['a','b'])
		# check exec
		self.assertEqual(x.exec(dict(a=a,b=b)), 3)
		
		s = 'a.x + b.y < 4'
		# computation initialization should fail
		self.assertEqual(Computation.initialize(s),None)
		x = Constraint.initialize(s)
		self.assertTrue(x is not None)
		# check object properties
		self.assertTrue(isinstance(x,Constraint))
		self.assertEqual(x.code,'a.x + b.y < 4')
		self.assertEqual(sorted(x.keywords),['a','b'])
		# check exec
		self.assertEqual(x.exec(dict(a=a,b=b)), True)

		r = '100'
		# constraint and computation initialization should fail
		self.assertEqual(Constraint.initialize(r),None)
		self.assertEqual(Computation.initialize(r),None)
		# rate law initialization should pass
		x = RateLaw.initialize(r)
		self.assertTrue(x is not None)
		# check object properties
		self.assertTrue(isinstance(x,RateLaw))
		self.assertEqual(x.code,'100')
		self.assertEqual(sorted(x.keywords),[])
		# check exec
		self.assertEqual(x.exec(), 100)	

		t = '"blah"'
		# constraint and computation initialization should fail
		self.assertEqual(Constraint.initialize(r),None)
		self.assertEqual(Computation.initialize(r),None)
		# rate law initialization should pass
		x = RateLaw.initialize(t)
		self.assertTrue(x is not None)
		# check object properties
		self.assertTrue(isinstance(x,RateLaw))
		self.assertEqual(x.code,'"blah"')
		self.assertEqual(sorted(x.keywords),[])
		# check exec
		with self.assertRaises(AssertionError):
			x.exec()
		
		### NOTABLE FAILURE and RESULTANT AMBIGUITY
		### To resolve set complicated expressions as v=expr
		### then use v as v==True or p.a.action(v)

		# s6 = "p.a.compute(x=y,p=q) != all(a.x,p.contains(x=z))"
		# u1 = "p.a.set_ph({0})".format(s6) 
		# In both cases, the parser is matching "q) != all(..."
		# as an expression
		# in s6, it incorrectly tries to parse as action
		# in u1, it incorrectly tries to parse as expression
		