"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import mol_schema
from wc_rules import exceptions
from wc_rules import rate_law
import unittest

class TestMolSchema(unittest.TestCase):
    
    def test_site(self):
        class A(mol_schema.Site):pass
        a = A(id='1')
        self.assertEqual(a.label, 'A')    
        self.assertEqual(a.id, '1')
        
        with self.assertRaises(exceptions.AddObjectError): a.add(object())
    
    def test_pairwise_overlap(self):
        class a(mol_schema.Site):pass
        class b(mol_schema.Site):pass
        class c(mol_schema.Site):pass
        
        a1,b1,c1 = a(),b(),c()
        self.assertEqual(a1.pairwise_overlap,None)
        
        a1.init_pairwise_overlap()
        self.assertEqual(a1.pairwise_overlap.source.label,'a')
        
        a1.add_pairwise_overlap_targets([b1,c1])
        self.assertEqual(a1.has_overlaps(), True)
        self.assertEqual(a1.pairwise_overlap.get_num_targets(), 2)
        self.assertEqual([x.label for x in a1.get_overlaps()],['b','c'])
        self.assertEqual([x.label for y in a1.get_overlaps() for x in y.get_overlaps()],['a','a'])
        
        a1.remove_pairwise_overlap_targets(c1)
        self.assertEqual([x.label for x in a1.get_overlaps()],['b'])
        
        a1.remove_pairwise_overlap_targets(b1)
        self.assertEqual(a1.has_overlaps(), False)
        
        a1.add([b1,c1],where='overlaps')
        self.assertEqual([x.label for x in a1.get_overlaps()],['b','c'])
        
        a1.undef_pairwise_overlap()
        self.assertEqual(a1.pairwise_overlap,None)
        
    def test_binding_state(self):
        class a(mol_schema.Site):pass
        class b(mol_schema.Site):pass
        class c(mol_schema.Site):pass
        
        a1,b1,c1 = a(),b(),c()
        self.assertEqual(a1.binding_state,None)
        
        a1.init_binding_state()
        self.assertEqual(a1.binding_state.source.label, 'a')
        self.assertEqual(a1.get_binding_state_value(), 'unbound')
        
        a1.add_bond(b1)
        self.assertEqual(a1.get_binding_state_value(), 'bound')
        self.assertEqual(a1.get_binding_partner().label,'b')
        self.assertEqual(a1.get_binding_partner().get_binding_partner().label,'a')
        
        with self.assertRaises(exceptions.Error): a1.add_bond(c1)
        
        a1.remove_bond()
        self.assertEqual(a1.get_binding_state_value(), 'unbound')
        self.assertEqual(b1.get_binding_state_value(), 'unbound')
        
        a1.add(b1,where='bond')
        self.assertEqual(a1.get_binding_state_value(), 'bound')
        self.assertEqual(b1.get_binding_state_value(), 'bound')
        
        a1.undef_binding_state()
        self.assertEqual(a1.binding_state,None)
            
    def test_state(self):
        class A(mol_schema.Site):pass
        class P(mol_schema.BooleanStateVariable):pass
        a,p = A(), P(id='1')
        self.assertEqual(p.label,'P')    
        self.assertEqual(p.id, '1')
        
        a.add(p)
        self.assertEqual([x.label for x in a.boolvars],['P'])
        
        p.set_true()
        self.assertEqual(p.value,True)
        
        p.set_false()
        self.assertEqual(p.value,False)
        
    def test_molecule(self):
        class A(mol_schema.Molecule):pass
        class B(mol_schema.Site):pass
        class C(mol_schema.Site):pass
        a,b,c = A(id='1'), B(), C()
        self.assertEqual(a.label,'A')
        
        a.add([b,c])
        self.assertEqual([x.label for x in a.sites],['B','C'])
        
        self.assertEqual(a.id,'1')
        
        with self.assertRaises(exceptions.AddObjectError): a.add(object())
        
        b = a.sites.get(label='B')
        self.assertEqual(b.label,'B')
        
    def test_complex(self):
        class A(mol_schema.Molecule):pass
        a1,a2 = A(id='1'), A(id='2')
        
        cplx = mol_schema.Complex(id='1').add([a1,a2])
        self.assertEqual([x.label for x in cplx.molecules],['A','A'])
        self.assertEqual(cplx.id,'1')
        
        with self.assertRaises(exceptions.AddObjectError): cplx.add(object())
        
        a = cplx.molecules.get(label='A',id='1')
        self.assertEqual(a.label, 'A')
        self.assertEqual(a.id, '1')        
        
    def test_bond_op(self):
        class A(mol_schema.Site):pass
        a1,a2 = A(id='1'), A(id='2')
        bnd_op = mol_schema.BondOperation().set_target([a1,a2])
        self.assertEqual([x.label for x in bnd_op.target],['A','A'])
        
        with self.assertRaises(exceptions.AddObjectError): bnd_op.set_target(object())
        
    def test_state_op(self):
        class P(mol_schema.BooleanStateVariable):pass
        p = P()
        state_op = mol_schema.BooleanStateOperation().set_target(p)
        self.assertEqual(state_op.target.label,'P')
        
        with self.assertRaises(exceptions.AddObjectError): state_op.set_target(object())
        with self.assertRaises(exceptions.AddObjectError): state_op.set_target([object(),])    
    
    def test_rate_expression(self):
        k1 = rate_law.Parameter(symbol='k1',value=1000.0)
        expr1 = rate_law.RateExpression(expression='k1*k2',parameters=[k1])
        self.assertEqual([expr1.expression,expr1.parameters.get().symbol,expr1.parameters.get().value],['k1*k2','k1',1000.0])
    
    def test_rule(self):
        class A(mol_schema.Molecule): pass
        class B(mol_schema.Molecule): pass
        class b(mol_schema.Site): pass
        class a(mol_schema.Site): pass
        class P(mol_schema.BooleanStateVariable):pass
        
        a1 = a()
        b1 = b().add( P() )
        A1 = A().add( a1  )
        B1 = B().add( b1  )
        
        reac1 = mol_schema.Complex().add(A1)
        reac2 = mol_schema.Complex().add(B1)
        op1 = mol_schema.AddBond().set_target([a1,b1])
        op2 = mol_schema.SetTrue().set_target(b1.boolvars.get())
        kf = rate_law.RateExpression(expression='kf')
        kr = rate_law.RateExpression(expression='kr')
        
        rule1 = mol_schema.Rule(reversible=True,forward=kf,reverse=kr).add([reac1,reac2,op1,op2])
         
        self.assertEqual([x.label for y in rule1.reactants for x in y.molecules],['A','B'])
        self.assertEqual([y.label for y in rule1.operations[0].target],['a','b'])
        self.assertEqual(rule1.operations[1].target.label,'P')
        self.assertEqual([rule1.forward.expression,rule1.reverse.expression],['kf','kr'])
        
    def test_graph_complex(self):
        class A(mol_schema.Molecule):pass
        class B(mol_schema.Molecule):pass
        class x(mol_schema.Site):pass
        class y(mol_schema.Site):pass
        class z(mol_schema.Site):pass
        
        A1, B1 = A(), B()
        x1, y1, z1 = x(), y(), z()
        p1, p2 = mol_schema.BooleanStateVariable(), mol_schema.BooleanStateVariable()
        c1 = mol_schema.Complex()
        
        A1.add(x1).add(y1.add(p1))
        B1.add(z1.add(p1))
        x1.add_bond(z1)
        y1.init_binding_state()
        c1.add([A1, B1])
            
        g = c1.get_graph()
        
        def get_node_label(graph,node): return graph.node[node]['obj'].label
        
        nodes1 = sorted([get_node_label(g, x) for x in g.nodes()])
        nodes2 = ['A', 'B', 'BindingState', 'BindingState', 'BindingState', 'BooleanStateVariable', 'Complex', 'x', 'y', 'z']
        
        edges1 = sorted([tuple([get_node_label(g, x) for x in edge]) for edge in g.edges()])
        edges2 = [
            ('A', 'x'), ('A', 'y'), ('B', 'z'), 
            ('BindingState', 'x'), ('BindingState', 'z'), 
            ('Complex', 'A'), ('Complex', 'B'), 
            ('x', 'BindingState'), ('y', 'BindingState'), 
            ('z', 'BindingState'), ('z', 'BooleanStateVariable'),
            ]
            
        self.assertEqual(nodes1, nodes2)
        self.assertEqual(edges2, edges2)
