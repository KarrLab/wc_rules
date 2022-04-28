from wc_rules.schema.entity import Entity
from wc_rules.schema.attributes import IntegerAttribute, OneToOneAttribute
from wc_rules.expressions.executable import Constraint, Computation, RateLaw
from wc_rules.modeling.rule import InstanceRateRule
from wc_rules.modeling.pattern import Pattern, GraphContainer
from wc_rules.schema.chem import Molecule, Site
from pprint import pformat
#from wc_rules.actions import parser

import math
import unittest

class A(Entity):
	x = IntegerAttribute()
	y = IntegerAttribute()

class P(Entity):
	a = OneToOneAttribute(A,related_name='p')
	b = OneToOneAttribute(A,related_name='q')


class TestRateLaw(unittest.TestCase):
	
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
		


class Lig(Molecule):
	pass

class Rec(Molecule):
	pass

class RecBindingSite(Site):
	pass

class LigBindingSite(Site):
	pass

class TestRuleBuild(unittest.TestCase):

	def test_rule_one(self):
		lignode = Lig('Lig',sites=[RecBindingSite('rec1'),RecBindingSite('rec2')])
		lig  = Pattern(
			parent = GraphContainer(lignode.get_connected()), 
			constraints = ['len(rec1.bond)==0','len(rec2.bond)==0']
			)
		recnode =Rec('Rec',sites=[LigBindingSite('lig')])
		rec = Pattern(
			parent = GraphContainer(recnode.get_connected()),
			constraints = ['len(lig.bond)==0']
			)
		# note two bonds being formed at the same time
		binding_rule = InstanceRateRule(
			name = 'binding_rule',
			reactants = dict(L=lig,R1=rec,R2=rec),
			actions = ['k = some_value','L.rec1.add_bond(R1.lig)','L.rec2.add_bond(R2.lig)'],
			rate_prefix = 'binding_constant',
			parameters = ['binding_constant','some_value']
			)

		d = {
			'L': {
				'Lig': Lig,
				'rec2': RecBindingSite,
				'rec1': RecBindingSite
			},
			'R1': {
				'Rec': Rec,
				'lig': LigBindingSite,
			},
			'R2': {
				'Rec': Rec,
				'lig': LigBindingSite,
			},
			'binding_constant': 'Parameter',
			'some_value': 'Parameter',
			'actions':  ['k = some_value','L.rec1.add_bond(R1.lig)','L.rec2.add_bond(R2.lig)'],
			'rate_prefix': 'binding_constant'
		}
		self.maxDiff=None
		#self.assertEqual(pformat(binding_rule.namespace),pformat(namespace))
		self.assertEqual(binding_rule.asdict(),d)
		self.assertEqual(binding_rule.get_rate_law(),'binding_constant*comb(L.count(),1)*comb(R1.count(),2)')



