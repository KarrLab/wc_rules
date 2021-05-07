"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-27
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules.schema import chem
import unittest


class A(chem.Molecule):pass
class X(chem.Site):
    allowed_molecule_types = (A,)
class B(chem.Molecule):pass
class Y(chem.Site):
    allowed_molecule_types = (B,)
class Z(chem.Site):pass

class TestChem(unittest.TestCase):
    def test_get_classnames(self):
        A1 = A()
        self.assertEqual(A.get_classnames(),['A','Molecule'])
        self.assertEqual(A1.get_classnames(),['A','Molecule'])

    def test_sites(self):
        A1 = A('A1')
        X1 = X('X1')
        X2 = X('X2')

        A1.sites.extend([X1,X2])
        self.assertEqual(A1.sites,[X1,X2])
        self.assertEqual(X1.molecule,A1)
        self.assertEqual(X2.molecule,A1)

        A1.sites.remove(X1)
        A1.sites.remove(X2)
        self.assertEqual(A1.sites,[])
        self.assertEqual(X1.molecule,None)
        self.assertEqual(X2.molecule,None)

        X1.molecule = A1
        self.assertEqual(A1.sites,[X1])
        self.assertEqual(X1.molecule,A1)

        X1.molecule=None
        self.assertEqual(A1.sites,[])
        self.assertEqual(X1.molecule,None)

    def test_bond(self):
        A1 = A('A1')
        X1 = X('X1')
        X2 = X('X2')
        A1.sites.extend([X1,X2])

        B1 = B('B1')
        Y1 = Y('Y1')
        Y2 = Y('Y2')
        B1.add_sites(Y1,Y2)


        X1.bond = Y1
        self.assertEqual(X1.bond,Y1)
        self.assertEqual(Y1.bond,X1)

        Y1.bond = None
        self.assertEqual(X1.bond,None)
        self.assertEqual(Y1.bond,None)

        return
