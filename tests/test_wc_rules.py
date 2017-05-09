from wc_rules import bioschema as bio
from wc_rules import ratelaw as rl
from wc_rules import utils
import unittest

class TestBioschema(unittest.TestCase):
	
	def test_site(self):
		class A(bio.Site):pass
		a = A()
		self.assertEqual(a.label,'A')
		
		a.set_id('1')
		self.assertEqual(a.id,'1')
		
		with self.assertRaises(utils.AddObjectError): a.add(object())
		
	def test_bond(self):
		class A(bio.Site):pass
		class B(bio.Site):pass
		a,b = A(), B()
		
		self.assertEqual([x.bond for x in [a,b]],[None,None])
		self.assertEqual([x.bound for x in [a,b]],[False,False])
		
		bnd = bio.Bond(sites=[a,b])
		self.assertEqual([x.label for x in bnd.sites],['A','B'])
		self.assertEqual([x.bound for x in bnd.sites],[True,True])
		
		bnd = bio.Bond().add([a,b])
		self.assertEqual([x.label for x in bnd.sites],['A','B'])
		
		bnd = bio.Bond().add(a).add(b)
		self.assertEqual([x.label for x in bnd.sites],['A','B'])
		
		bnd.set_id('1')
		self.assertEqual(bnd.id,'1')
		
		with self.assertRaises(utils.AddObjectError): bnd.add(object())
		
		a = bnd.sites.get(label='A')
		self.assertEqual(a.label,'A')
		
	def test_exclusion(self):
		class A(bio.Site):pass
		class B(bio.Site):pass
		class C(bio.Site):pass
		a,b,c = A(), B(), C()
		
		exc = bio.Exclusion().add([a,c])
		self.assertEqual(c.available_to_bind,True)
		self.assertEqual([x.label for x in exc.sites],['A','C'])
		self.assertEqual([y.label for x in exc.sites for y in x.get_excludes() ], ['C','A'] )
		
		bnd  = bio.Bond().add([a,b])
		self.assertEqual(c.available_to_bind,False)
		
		exc.set_id('1')
		self.assertEqual(exc.id,'1')
		
		with self.assertRaises(utils.AddObjectError): exc.add(object())
		
		a = exc.sites.get(label='A')
		self.assertEqual(a.label,'A')
		
	def test_state(self):
		class A(bio.Site):pass
		class P(bio.BooleanStateVariable):pass
		a,p = A(), P()
		self.assertEqual(p.label,'P')
		
		p.set_id('1')
		self.assertEqual(p.id,'1')
		
		a.add(p)
		self.assertEqual([x.label for x in a.boolvars],['P'])
		
		p.set_true()
		self.assertEqual(p.value,True)
		
		p.set_false()
		self.assertEqual(p.value,False)
		
	def test_molecule(self):
		class A(bio.Molecule):pass
		class B(bio.Site):pass
		class C(bio.Site):pass
		a,b,c = A(), B(), C()
		self.assertEqual(a.label,'A')
		
		a.add([b,c])
		self.assertEqual([x.label for x in a.sites],['B','C'])
		
		a.set_id('1')
		self.assertEqual(a.id,'1')
		
		exc = bio.Exclusion().add([b,c])
		a = A().add(b).add(c).add(exc)
		self.assertEqual([x.label for x in a.sites],['B','C'])
		self.assertEqual([x.label for x in a.exclusions[0].sites],['B','C'])
		
		with self.assertRaises(utils.AddObjectError): a.add(object())
		
		b = a.sites.get(label='B')
		self.assertEqual(b.label,'B')
		b = exc.sites.get(label='B')
		self.assertEqual(b.label,'B')
		
	def test_complex(self):
		class A(bio.Molecule):pass
		class B(bio.Site):pass
		a1,a2,b1,b2 = A().set_id('1'), A().set_id('2'), B().set_id('1'), B().set_id('2')
		a1.add(b1)
		a2.add(b2)
		bnd = bio.Bond().add([b1,b2])
		
		cplx = bio.Complex().add([a1,a2,bnd])
		self.assertEqual([x.label for x in cplx.molecules],['A','A'])
		self.assertEqual([x.label for bnd in cplx.bonds for x in bnd.sites],['B','B'])
		
		cplx = bio.Complex().add(a1).add(a2).add(bnd)
		self.assertEqual([x.label for x in cplx.molecules],['A','A'])
		self.assertEqual([x.label for bnd in cplx.bonds for x in bnd.sites],['B','B'])
		
		cplx.set_id('1')
		self.assertEqual(cplx.id,'1')
		
		with self.assertRaises(utils.AddObjectError): cplx.add(object())
		
		a = cplx.molecules.get(label='A',id='1')
		self.assertEqual([a.label,a.id],['A','1'])
		
		b = cplx.bonds.get().sites.get(label='B',id='1')
		self.assertEqual([b.label,b.id],['B','1'])
		
	def test_bond_op(self):
		class A(bio.Site):pass
		a1,a2 = A().set_id('1'), A().set_id('2')
		bnd_op = bio.BondOperation().set_target([a1,a2])
		self.assertEqual([x.label for x in bnd_op.target],['A','A'])
		
		with self.assertRaises(utils.AddObjectError): bnd_op.set_target(object())
		
	def test_state_op(self):
		class P(bio.BooleanStateVariable):pass
		p = P()
		state_op = bio.BooleanStateOperation().set_target(p)
		self.assertEqual(state_op.target.label,'P')
		
		with self.assertRaises(utils.AddObjectError): state_op.set_target(object())
		with self.assertRaises(utils.AddObjectError): state_op.set_target([object(),])	
	
	def test_rate_expression(self):
		
		k1 = rl.Parameter(symbol='k1',value=1000.0)
		expr1 = rl.RateExpression(expr='k1*k2',parameters=[k1])
		self.assertEqual([expr1.expr,expr1.parameters.get().symbol,expr1.parameters.get().value],['k1*k2','k1',1000.0])
	
	def test_rule(self):
		class A(bio.Molecule): pass
		class B(bio.Molecule): pass
		class b(bio.Site): pass
		class a(bio.Site): pass
		class P(bio.BooleanStateVariable):pass
		
		a1 = a()
		b1 = b().add( P() )
		A1 = A().add( a1  )
		B1 = B().add( b1  )
		
		reac1 = bio.Complex().add(A1)
		reac2 = bio.Complex().add(B1)
		op1 = bio.AddBond().set_target([a1,b1])
		op2 = bio.Phosphorylate().set_target(b1.boolvars.get())
		kf = rl.RateExpression(expr='kf')
		kr = rl.RateExpression(expr='kr')
		
		rule1 = bio.Rule(reversible=True,forward=kf,reverse=kr).add([reac1,reac2,op1,op2])
 		
		self.assertEqual([x.label for y in rule1.reactants for x in y.molecules],['A','B'])
		self.assertEqual([y.label for y in rule1.operations[0].target],['a','b'])
		self.assertEqual(rule1.operations[1].target.label,'P')
		self.assertEqual([rule1.forward.expr,rule1.reverse.expr],['kf','kr'])
		
	def test_pairwise_overlaps(self):
		class a(bio.Site): pass
		class b(bio.Site): pass
		class M(bio.Molecule): pass
		
		a1,b1,b2 = a(),b(),b()
	
		a1.add_pairwise_overlaps([b1,b2])
		self.assertEqual(a1.pairwise_overlaps_obj.sites,[b1,b2])
		self.assertEqual(a1,b1.pairwise_overlaps_obj.sites[0])
		self.assertEqual(a1,b2.pairwise_overlaps_obj.sites[0])
		
		a1,b1,b2 = a(),b(),b()
		a1.add_pairwise_overlaps([b1,b2],mutual=False)
		self.assertEqual(a1.pairwise_overlaps_obj.sites,[b1,b2])
		self.assertEqual(None,b1.pairwise_overlaps_obj)
		self.assertEqual(None,b2.pairwise_overlaps_obj)
		
		m1 = M()
		with self.assertRaises(utils.AddObjectError): a1.add_pairwise_overlaps(m1)
	
	def test_current(self):
		print("\n\nOutput goes here\n===============\n")
		print("\n===============\nOutput ends here\n")
	
	
		
