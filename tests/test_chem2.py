"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-27
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import chem2,utils
import unittest


class A(chem2.Molecule):pass
class X(chem2.Site):
    allowed_molecule_types = (A,)
class B(chem2.Molecule):pass
class Y(chem2.Site):
    allowed_molecule_types = (B,)
class Z(chem2.Site):pass
class NewBond(chem2.Bond):
    allowed_target_types = (X,Y,)

class TestBase(unittest.TestCase):
    def test_sites(self):
        A1 = A().set_id('A1')
        X1 = X().set_id('X1')
        X2 = X().set_id('X2')

        A1.add_sites(X1,X2)
        self.assertEqual(A1.sites,[X1,X2])
        self.assertEqual(X1.molecule,A1)
        self.assertEqual(X2.molecule,A1)

        A1.remove_sites(X1,X2)
        self.assertEqual(A1.sites,[])
        self.assertEqual(X1.molecule,None)
        self.assertEqual(X2.molecule,None)

        X1.set_molecule(A1)
        self.assertEqual(A1.sites,[X1])
        self.assertEqual(X1.molecule,A1)

        X1.unset_molecule()
        self.assertEqual(A1.sites,[])
        self.assertEqual(X1.molecule,None)

        Y1 = Y().set_id('Y1')
        with self.assertRaises(utils.ValidateError):
            A1.add_sites(Y1)
            Y1.verify_molecule_type()
        return

    def test_site_relation(self):
        A1 = A().set_id('A1')
        X1 = X().set_id('X1')
        X2 = X().set_id('X2')
        A1.add_sites(X1,X2)

        B1 = B().set_id('B1')
        Y1 = Y().set_id('Y1')
        Y2 = Y().set_id('Y2')
        B1.add_sites(Y1,Y2)

        bnd1 = chem2.Bond()
        with self.assertRaises(utils.ValidateError):
            bnd1.add_sources(X1)
            bnd1.verify_maximum_sources()
        bnd1.remove_sources(X1)
        self.assertEqual(bnd1.sources,[])

        bnd1 = chem2.Bond().add_targets(X1,Y1)
        self.assertEqual(bnd1.get_targets(),[X1,Y1])
        self.assertEqual(X1.get_bond(),bnd1)
        self.assertEqual(Y1.get_bond(),bnd1)
        bnd1.verify_maximum_targets()

        with self.assertRaises(utils.ValidateError):
            bnd1.add_targets(Y2)
            bnd1.verify_maximum_targets()
        bnd1.remove_targets(Y2)
        self.assertEqual(bnd1.get_targets(),[X1,Y1])

        with self.assertRaises(utils.ValidateError):
            bnd2 = chem2.Bond().add_targets(X1)
            X1.verify_maximum_allowed_relations_as_a_target()
        bnd2.remove_targets(X1)

        Z1 = Z()
        with self.assertRaises(utils.ValidateError):
            bnd = NewBond().add_targets(Z1)
            bnd.verify_target_types()

        return
