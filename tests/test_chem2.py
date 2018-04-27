"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-27
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import chem2,utils
import unittest


class A(chem2.Molecule):pass
class X(chem2.Site):pass
class B(chem2.Molecule):pass
class Y(chem2.Site):pass

class TestBase(unittest.TestCase):
    def test_site_relations(self):

        A1 = A().set_id('A1').add_sites(
            X().set_id('X1'),
            X().set_id('X2')
        )

        B1 = B().set_id('B1').add_sites(
            Y().set_id('Y1'),
            Y().set_id('Y2'),
        )

        bnd1 = chem2.Bond()
        with self.assertRaises(utils.AddError):
            bnd1.add_sources(A1.sites.get_one(id='X1'))

        bnd1.add_targets(
            A1.sites.get_one(id='X1'),
            B1.sites.get_one(id='Y1'),
        )

        with self.assertRaises(utils.AddError):
            bnd1.add_targets(B1.sites.get_one(id='Y2'))

        with self.assertRaises(utils.AddError):
            bnd2 = chem2.Bond().add_targets(A1.sites.get_one(id='X1'))

        return
