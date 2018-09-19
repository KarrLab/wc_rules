from wc_rules import utils,chem
from wc_rules.species import Species, SpeciesFactory
from obj_model import core
from collections import Counter

import unittest

class A(chem.Molecule):pass
class X(chem.Site):
    ph1 = core.BooleanAttribute(default=None)
    ph2 = core.BooleanAttribute(default=None)


class TestPattern(unittest.TestCase):

    def test_species_init(self):
        a1 = A()
        x1 = X(ph1=True,ph2=True)
        x2 = X(ph1=True,ph2=True)
        a1.add_sites(x1,x2)
        s1 = Species('s1').add_node(a1,recurse=True)
        self.assertEqual(len(s1),3)

    def test_species_factory(self):
        a1 = A(id='a')
        x1 = X(id='x',ph1=True,ph2=True)
        a1.add_sites(x1)
        s1 = Species('s1').add_node(a1,recurse=True)

        a2 = A(id='a')
        x2 = X(id='x',ph1=True,ph2=False)
        a2.add_sites(x2)
        s2 = Species('s2').add_node(a2,recurse=True)

        factory1 = SpeciesFactory().add_species(s1)
        sp_list =list(factory1.generate(100,preserve_ids=True))

        c = Counter(x._nodes['a'].label for x in sp_list)
        self.assertEqual(c['A'],100)

        c = Counter(x._nodes['x'].label for x in sp_list)
        self.assertEqual(c['X'],100)

        c = Counter(x._nodes['x'].ph1 for x in sp_list)
        self.assertEqual(c[True],100)

        c = Counter(x._nodes['x'].ph2 for x in sp_list)
        self.assertEqual(c[True],100)
        del sp_list

        factory2 = SpeciesFactory()
        factory2.add_species(s1,weight=1)
        factory2.add_species(s2,weight=2)
        sp_list =list(factory2.generate(100,preserve_ids=True))

        c = Counter(x._nodes['x'].ph1 for x in sp_list)
        self.assertEqual(c[True],100)

        c = Counter(x._nodes['x'].ph2 for x in sp_list)
        self.assertTrue(c[True] < 50)
