from obj_model import core
from wc_rules import utils,chem
from wc_rules.pattern import Pattern
import unittest

class A(chem.Molecule):pass
class X(chem.Site):
    ph1 = core.BooleanAttribute(default=None)
    ph2 = core.BooleanAttribute(default=None)
class Y(chem.Site):
    ph = core.BooleanAttribute(default=None)
    v = core.IntegerAttribute(default=None)

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
        p1_ids = sorted([x.id for x in p1])
        p2_ids = sorted([x.id for x in p2])
        self.assertEqual(p1_ids,p2_ids)

    def test_generate_queries(self):
        a = A(id='a')
        y1 = Y(id='y1',ph=True,v=0)
        y2 = Y(id='y2',ph=False,v=-5)
        a.add_sites(y1,y2)

        p = Pattern('p').add_node(a,recurse=True)

        qdict = p.generate_queries()

        self.assertEqual(sorted(list(qdict.keys())), ['attr','rel','type'])

        for idx in qdict['type']:
            node = p[idx]
            tuplist = qdict['type'][idx]
            for tup in tuplist:
                _class = tup[1]
                self.assertTrue(isinstance(node,_class))

        for idx in qdict['attr']:
            node = p[idx]
            tuplist = qdict['attr'][idx]
            for tup in tuplist:
                attr = tup[1]
                op = tup[2]
                value = tup[3]
                self.assertTrue(op(getattr(node,attr),value))

        for tup in qdict['rel']:
            idx1 = tup[1]
            attr1 = tup[2]
            attr2 = tup[3]
            idx2 = tup[4]

            node1 = p[idx1]
            node2 = p[idx2]
            self.assertTrue(node1 in utils.listify(getattr(node2,attr2)))
            self.assertTrue(node2 in utils.listify(getattr(node1,attr1)))
