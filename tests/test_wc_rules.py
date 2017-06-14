from wc_rules import bio
from wc_rules import chem
from wc_rules import ratelaw as rl
from wc_rules import utils
import unittest

class TestBioschema(unittest.TestCase):
	
	def test_site(self):
		class A(chem.Site):pass
		a = A()
		self.assertEqual(a.label,'A')
		
		a.set_id('1')
		self.assertEqual(a.id,'1')
		
		with self.assertRaises(utils.AddObjectError): a.add(object())
	
	def test_pairwise_overlap(self):
		class a(chem.Site):pass
		class b(chem.Site):pass
		class c(chem.Site):pass
		
		a1,b1,c1 = a(),b(),c()
		self.assertEqual(a1.pairwise_overlap,None)
		
		a1.init_pairwise_overlap()
		self.assertEqual(a1.pairwise_overlap.source.label,'a')
		
		a1.add_pairwise_overlap_targets([b1,c1])
		self.assertEqual(a1.has_overlaps,True)
		self.assertEqual(a1.pairwise_overlap.n_targets,2)
		self.assertEqual([x.label for x in a1.get_overlaps()],['b','c'])
		self.assertEqual([x.label for y in a1.get_overlaps() for x in y.get_overlaps()],['a','a'])
		
		a1.remove_pairwise_overlap_targets(c1)
		self.assertEqual([x.label for x in a1.get_overlaps()],['b'])
		
		a1.remove_pairwise_overlap_targets(b1)
		self.assertEqual(a1.has_overlaps,False)
		
		a1.add([b1,c1],where='overlaps')
		self.assertEqual([x.label for x in a1.get_overlaps()],['b','c'])
		
		a1.undef_pairwise_overlap()
		self.assertEqual(a1.pairwise_overlap,None)
		
	def test_binding_state(self):
		class a(chem.Site):pass
		class b(chem.Site):pass
		class c(chem.Site):pass
		
		a1,b1,c1 = a(),b(),c()
		self.assertEqual(a1.binding_state,None)
		
		a1.init_binding_state()
		self.assertEqual(a1.binding_state.source.label,'a')
		self.assertEqual(a1.binding_state_value,'unbound')
		
		a1.add_bond_to(b1)
		self.assertEqual(a1.binding_state_value,'bound')
		self.assertEqual(a1.get_binding_partner().label,'b')
		self.assertEqual(a1.get_binding_partner().get_binding_partner().label,'a')
		
		with self.assertRaises(utils.GenericError): a1.add_bond_to(c1)
		
		a1.remove_bond()
		self.assertEqual([a1.binding_state_value,b1.binding_state_value],['unbound','unbound'])
		
		a1.add(b1,where='bond')
		self.assertEqual([a1.binding_state_value,b1.binding_state_value],['bound','bound'])
		
		a1.undef_binding_state()
		self.assertEqual(a1.binding_state,None)
			
	def test_state(self):
		class A(chem.Site):pass
		class P(chem.BooleanStateVariable):pass
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
		class A(chem.Molecule):pass
		class B(chem.Site):pass
		class C(chem.Site):pass
		a,b,c = A(), B(), C()
		self.assertEqual(a.label,'A')
		
		a.add([b,c])
		self.assertEqual([x.label for x in a.sites],['B','C'])
		
		a.set_id('1')
		self.assertEqual(a.id,'1')
		
		with self.assertRaises(utils.AddObjectError): a.add(object())
		
		b = a.sites.get(label='B')
		self.assertEqual(b.label,'B')
		
	def test_complex(self):
		class A(chem.Molecule):pass
		a1,a2 = A().set_id('1'), A().set_id('2')
		
		cplx = chem.Complex().add([a1,a2])
		self.assertEqual([x.label for x in cplx.molecules],['A','A'])
		
		cplx.set_id('1')
		self.assertEqual(cplx.id,'1')
		
		with self.assertRaises(utils.AddObjectError): cplx.add(object())
		
		a = cplx.molecules.get(label='A',id='1')
		self.assertEqual([a.label,a.id],['A','1'])
		
		
	def test_bond_op(self):
		class A(chem.Site):pass
		a1,a2 = A().set_id('1'), A().set_id('2')
		bnd_op = chem.BondOperation().set_target([a1,a2])
		self.assertEqual([x.label for x in bnd_op.target],['A','A'])
		
		with self.assertRaises(utils.AddObjectError): bnd_op.set_target(object())
		
	def test_state_op(self):
		class P(chem.BooleanStateVariable):pass
		p = P()
		state_op = chem.BooleanStateOperation().set_target(p)
		self.assertEqual(state_op.target.label,'P')
		
		with self.assertRaises(utils.AddObjectError): state_op.set_target(object())
		with self.assertRaises(utils.AddObjectError): state_op.set_target([object(),])	
	
	def test_rate_expression(self):
		k1 = rl.Parameter(symbol='k1',value=1000.0)
		expr1 = rl.RateExpression(expr='k1*k2',parameters=[k1])
		self.assertEqual([expr1.expr,expr1.parameters.get().symbol,expr1.parameters.get().value],['k1*k2','k1',1000.0])
	
	def test_rule(self):
		class A(chem.Molecule): pass
		class B(chem.Molecule): pass
		class b(chem.Site): pass
		class a(chem.Site): pass
		class P(chem.BooleanStateVariable):pass
		
		a1 = a()
		b1 = b().add( P() )
		A1 = A().add( a1  )
		B1 = B().add( b1  )
		
		reac1 = chem.Complex().add(A1)
		reac2 = chem.Complex().add(B1)
		op1 = chem.AddBond().set_target([a1,b1])
		op2 = bio.Phosphorylate().set_target(b1.boolvars.get())
		kf = rl.RateExpression(expr='kf')
		kr = rl.RateExpression(expr='kr')
		
		rule1 = chem.Rule(reversible=True,forward=kf,reverse=kr).add([reac1,reac2,op1,op2])
 		
		self.assertEqual([x.label for y in rule1.reactants for x in y.molecules],['A','B'])
		self.assertEqual([y.label for y in rule1.operations[0].target],['a','b'])
		self.assertEqual(rule1.operations[1].target.label,'P')
		self.assertEqual([rule1.forward.expr,rule1.reverse.expr],['kf','kr'])
		
	def test_graph_complex(self):
		class A(chem.Molecule):pass
		class B(chem.Molecule):pass
		class x(chem.Site):pass
		class y(chem.Site):pass
		class z(chem.Site):pass
		
		A1, B1 = A(), B()
		x1, y1, z1 = x(), y(), z()
		p1, p2 = bio.PhosphorylationState(), bio.PhosphorylationState()
		c1 = chem.Complex()
		
		A1.add(x1).add(y1.add(p1))
		B1.add(z1.add(p1))
		x1.add_bond_to(z1)
		y1.init_binding_state()
		c1.add([A1,B1])
			
		g = c1.graph
		
		def get_node_label(graph,node): return graph.node[node]['obj'].label
		
		nodes1 = sorted([get_node_label(g,x) for x in g.nodes()])
		nodes2 = ['A', 'B', 'BindingState', 'BindingState', 'BindingState', 'Complex', 'PhosphorylationState', 'x', 'y', 'z']
		
		edges1 = sorted([tuple([get_node_label(g,x) for x in edge]) for edge in g.edges()])
		edges2 = [('A', 'x'), ('A', 'y'), ('B', 'z'), ('BindingState', 'x'), ('BindingState', 'z'), ('Complex', 'A'), ('Complex', 'B'), ('x', 'BindingState'), ('y', 'BindingState'), ('z', 'BindingState'), ('z', 'PhosphorylationState')]
			
		self.assertEqual(nodes1,nodes2)
		self.assertEqual(edges2,edges2)
			
		
	def test_current(self):pass
	
	
		
