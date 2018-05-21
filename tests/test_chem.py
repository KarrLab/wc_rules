"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-27
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import chem,utils
import unittest


class A(chem.Molecule):pass
class X(chem.Site):
    allowed_molecule_types = (A,)
class B(chem.Molecule):pass
class Y(chem.Site):
    allowed_molecule_types = (B,)
class Z(chem.Site):pass
class NewBond(chem.Bond):
    allowed_site_types = (X,Y,)

class TestBase(unittest.TestCase):
    def test_get_classnames(self):
        A1 = A()
        self.assertEqual(A.get_classnames(),['A','Molecule'])
        self.assertEqual(A1.get_classnames(),['A','Molecule'])

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
            Y1.verify_allowed_molecule_type()
        return

    def test_bond(self):
        A1 = A().set_id('A1')
        X1 = X().set_id('X1')
        X2 = X().set_id('X2')
        A1.add_sites(X1,X2)

        B1 = B().set_id('B1')
        Y1 = Y().set_id('Y1')
        Y2 = Y().set_id('Y2')
        B1.add_sites(Y1,Y2)


        bnd1 = chem.Bond().add_sites(X1,Y1)
        self.assertEqual(bnd1.get_sites(),[X1,Y1])
        self.assertEqual(X1.get_bond(),bnd1)
        self.assertEqual(Y1.get_bond(),bnd1)
        bnd1.verify_maximum_number_of_sites()

        with self.assertRaises(utils.ValidateError):
            bnd1.add_sites(Y2)
            bnd1.verify_maximum_number_of_sites()
        bnd1.remove_sites(Y2)
        self.assertEqual(bnd1.get_sites(),[X1,Y1])

        Z1 = Z()
        with self.assertRaises(utils.ValidateError):
            bnd = NewBond().add_sites(Z1)
            bnd.verify_allowed_site_types()

        return

    def test_overlaps(self):
        A1 = A().set_id('A1')
        X1 = X().set_id('X1')
        X2 = X().set_id('X2')
        A1.add_sites(X1,X2)

        olp1 = chem.Overlap().add_sites(X1,X2)
        self.assertEqual(olp1.get_sites(),[X1,X2])
        self.assertEqual(X1.get_overlaps()[0],olp1)
        self.assertEqual(X2.get_overlaps()[0],olp1)
        olp1.remove_sites(X1,X2)
        self.assertEqual(len(olp1.get_sites()),0)
        X1.add_overlaps(olp1)
        X2.add_overlaps(olp1)
        self.assertEqual(olp1.get_sites(),[X1,X2])
        X1.remove_overlaps(olp1)
        X2.remove_overlaps(olp1)
        self.assertEqual(len(olp1.get_sites()),0)
        return
