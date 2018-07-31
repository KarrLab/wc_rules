from obj_model import core
from wc_rules import utils,chem
from wc_rules.pattern import Pattern
import unittest

class A(chem.Molecule):pass
class X(chem.Site):
    ph1 = core.BooleanAttribute(default=None)
    ph2 = core.BooleanAttribute(default=None)



class TestPattern(unittest.TestCase):

    def test_pattern_init(self):
        a1 = A(id='a1')
        x1 = X(id='x1')
        x2 = X(id='x2')
        a1.add_sites(x1,x2)

        p1 = Pattern('p1')
        self.assertTrue(len(p1)==0)
        p1.add_node(x1,recurse=False)
        self.assertTrue(len(p1)==1)
        del p1

        p1 = Pattern('p1',nodelist=[a1],recurse=True)
        self.assertTrue(len(p1)==3)
        del p1

        p1 = Pattern('p1',nodelist=[x1])
        self.assertTrue(len(p1)==3)

        p2 = p1.duplicate()
        self.assertTrue(len(p2)==3)

        p2 = p1.duplicate(preserve_ids=True)
        self.assertTrue(len(p2)==3)
        self.assertEquals(sorted(p1._nodes.keys()), sorted(p2._nodes.keys()))
        
