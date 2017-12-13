"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import bio
from wc_rules import chem
from wc_rules import ratelaw
from wc_rules import utils
from wc_rules import variables
import unittest


class TestBioschema(unittest.TestCase):

    def test_site(self):
        class MySite(chem.Site):
            pass

        my_site = MySite()
        self.assertEqual(my_site.label, 'MySite')

        my_site.set_id('1')
        self.assertEqual(my_site.id, '1')

    def test_pairwise_overlap(self):
        class a(chem.Site):
            pass
        class b(chem.Site):
            pass
        class c(chem.Site):
            pass

        a1, b1, c1 = a(), b(), c()
        self.assertEqual(a1.overlaps, [])
        self.assertEqual(a1.has_overlaps(), False)

        a1.add_overlaps([b1, c1], mutual=True)
        self.assertEqual(a1.has_overlaps(), True)
        self.assertEqual(len(a1.overlaps), 2)
        self.assertEqual([x.label for x in a1.get_overlaps()], ['b', 'c'])
        self.assertEqual([x.label for y in a1.get_overlaps() for x in y.get_overlaps()], ['a', 'a'])

        a1.remove_overlaps(c1)
        self.assertEqual(a1.overlaps, [b1])
        self.assertEqual([x.label for x in a1.get_overlaps()], ['b'])

        a1.remove_overlaps(b1)
        self.assertEqual(a1.overlaps, [])
        self.assertEqual(a1.has_overlaps(), False)

        a1.add_overlaps([b1, c1])
        self.assertEqual([x.label for x in a1.get_overlaps()], ['b', 'c'])

        a1.undef_overlaps()
        self.assertEqual(a1.overlaps, [])

    def test_binding_state(self):
        class a(chem.Site):
            pass
        class b(chem.Site):
            pass
        class c(chem.Site):
            pass

        a1 = a()
        b1 = b()
        c1 = c()
        self.assertEqual(a1.bond, None)

        a1.sync_binding_state()
        b1.sync_binding_state()
        c1.sync_binding_state()
        self.assertEqual(a1.bond, None)
        self.assertEqual(a1.binding_state_value, None)
        self.assertEqual(a1.get_binding_partner(), None)

        a1.add_bond_to(b1)
        self.assertEqual(a1.binding_state_value, 'bound')
        self.assertEqual(a1.get_binding_partner().label, 'b')
        self.assertEqual(a1.get_binding_partner().get_binding_partner().label, 'a')

        a1.add_bond_to(c1)
        self.assertEqual(a1.bond, c1)
        self.assertEqual(a1.binding_state_value, 'bound')
        self.assertEqual(a1.get_binding_partner().label, 'c')
        self.assertEqual(a1.get_binding_partner().get_binding_partner().label, 'a')
        self.assertEqual(b1.bond, None)
        self.assertEqual(b1.binding_state_value, None)
        self.assertEqual(b1.get_binding_partner(), None)

        a1.remove_bond()
        self.assertEqual(a1.binding_state_value, 'unbound')
        self.assertEqual(b1.binding_state_value, None)
        self.assertEqual(c1.binding_state_value, 'unbound')

        a1.add_bond_to(b1)
        self.assertEqual(a1.binding_state_value, 'bound')
        self.assertEqual(b1.binding_state_value, 'bound')

        a1.undef_binding_state()
        self.assertEqual(a1.binding_state_value, None)

    def test_state(self):
        class A(chem.Site):
            pass
        class P(variables.BooleanVariable):
            pass

        a = A()
        p = P()
        self.assertEqual(p.label, 'P')

        p.set_id('1')
        self.assertEqual(p.id, '1')

        a.boolvars.append(p)
        self.assertEqual([x.label for x in a.boolvars], ['P'])

        p.set_true()
        self.assertEqual(p.value, True)

        p.set_false()
        self.assertEqual(p.value, False)

    def test_molecule(self):
        class A(chem.Molecule):
            pass
        class B(chem.Site):
            pass
        class C(chem.Site):
            pass

        a = A()
        b = B()
        c = C()
        self.assertEqual(a.label, 'A')

        a.sites = [b, c]
        self.assertEqual([x.label for x in a.sites], ['B', 'C'])

        a.set_id('1')
        self.assertEqual(a.id, '1')

        b = a.sites.get(label='B')
        self.assertEqual(b.label, 'B')

    def test_complex(self):
        class A(chem.Molecule):
            pass

        a1 = A().set_id('1')
        a2 = A().set_id('2')

        cplx = chem.Complex()
        cplx.molecules.extend([a1, a2])
        self.assertEqual(cplx.molecules, [a1, a2])
        self.assertEqual([mol.label for mol in cplx.molecules], ['A', 'A'])

        cplx.set_id('1')
        self.assertEqual(cplx.id, '1')

        a = cplx.molecules.get(label='A', id='1')
        self.assertEqual([a.label, a.id], ['A', '1'])

    def test_bond_op(self):
        class A(chem.Site):
            pass

        a1 = A().set_id('1')
        a2 = A().set_id('2')

        bnd_op = chem.BondOperation().set_target([a1, a2])
        self.assertEqual([x.label for x in bnd_op.target], ['A', 'A'])

        with self.assertRaises(utils.AddObjectError):
            bnd_op.set_target(object())

    def test_bond_op_2(self):
        class MySite(chem.Site):
            pass

        bond_op = chem.BondOperation()

        my_site = MySite()
        my_site2 = MySite()
        my_site3 = MySite()

        bond_op.target = [my_site]
        self.assertEqual(bond_op.sites, [my_site])
        self.assertEqual(bond_op.target, [my_site])

        bond_op.set_target(my_site2)
        self.assertEqual(bond_op.sites, [my_site, my_site2])
        self.assertEqual(bond_op.target, [my_site, my_site2])

        bond_op.set_target([my_site2, my_site3])
        self.assertEqual(bond_op.sites, [my_site, my_site2, my_site3])
        self.assertEqual(bond_op.target, [my_site, my_site2, my_site3])

        bond_op.sites = [my_site2, my_site3]
        self.assertEqual(bond_op.sites, [my_site2, my_site3])
        self.assertEqual(bond_op.target, [my_site2, my_site3])

        with self.assertRaises(utils.AddObjectError):
            bond_op.set_target(object())

    def test_state_op(self):
        class P(variables.BooleanVariable):
            pass

        p = P()

        state_op = chem.BooleanStateOperation()
        state_op.set_target(p)
        self.assertEqual(state_op.target.label, 'P')

        with self.assertRaises(utils.AddObjectError):
            state_op.set_target(object())
        with self.assertRaises(utils.AddObjectError):
            state_op.set_target([object(), ])

    def test_rate_expression(self):
        k1 = ratelaw.Parameter(symbol='k1', value=1000.0)
        expr1 = ratelaw.RateExpression(expr='k1*k2', parameters=[k1])
        self.assertEqual([expr1.expr, expr1.parameters.get().symbol, expr1.parameters.get().value], ['k1*k2', 'k1', 1000.0])

    def test_rule(self):
        class A(chem.Molecule):
            pass
        class B(chem.Molecule):
            pass
        class b(chem.Site):
            pass
        class a(chem.Site):
            pass
        class P(variables.BooleanVariable):
            pass

        a1 = a()
        b1 = b()
        A1 = A()
        B1 = B()
        b1.boolvars.append(P())
        A1.sites.append(a1)
        B1.sites.append(b1)

        reac1 = chem.Complex()
        reac2 = chem.Complex()
        reac1.molecules.append(A1)
        reac2.molecules.append(B1)

        op1 = chem.AddBond().set_target([a1, b1])
        op2 = bio.Phosphorylate().set_target(b1.boolvars.get())
        kf = ratelaw.RateExpression(expr='kf')
        kr = ratelaw.RateExpression(expr='kr')

        rule1 = chem.Rule(reversible=True, forward=kf, reverse=kr)
        rule1.reactants.extend([reac1, reac2])
        rule1.operations.extend([op1, op2])

        self.assertEqual([x.label for y in rule1.reactants for x in y.molecules], ['A', 'B'])
        self.assertEqual([y.label for y in rule1.operations[0].target], ['a', 'b'])
        self.assertEqual(rule1.operations[1].target.label, 'P')
        self.assertEqual([rule1.forward.expr, rule1.reverse.expr], ['kf', 'kr'])

    def test_graph_complex(self):
        class A(chem.Molecule):
            pass
        class B(chem.Molecule):
            pass
        class x(chem.Site):
            pass
        class y(chem.Site):
            pass
        class z(chem.Site):
            pass

        A1, B1 = A(), B()
        x1, y1, z1 = x(), y(), z()
        p1, p2 = bio.PhosphorylationState(), bio.PhosphorylationState()
        c1 = chem.Complex()

        A1.sites.append(x1)
        A1.sites.append(y1)
        B1.sites.append(z1)
        x1.add_bond_to(z1)
        y1.boolvars.append(p1)
        z1.boolvars.append(p1)
        y1.sync_binding_state()
        c1.molecules.extend([A1, B1])

        g = c1.graph

        def get_node_label(graph, node):
            return graph.node[node]['obj'].label

        nodes1 = sorted([get_node_label(g, x) for x in g.nodes()])
        nodes2 = ['A', 'B', 'Complex', 'PhosphorylationState', 'x', 'y', 'z']

        edges1 = sorted([tuple([get_node_label(g, x) for x in edge]) for edge in g.edges()])
        edges2 = [('A', 'x'), ('A', 'y'), ('B', 'z'), ('BindingState', 'x'), ('BindingState', 'z'), ('Complex', 'A'),
                  ('Complex', 'B'), ('x', 'BindingState'), ('y', 'BindingState'), ('z', 'BindingState'), ('z', 'PhosphorylationState')]

        self.assertEqual(nodes1, nodes2)
        self.assertEqual(edges2, edges2)
