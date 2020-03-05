from obj_tables import core
from wc_rules import utils, chem
from wc_rules.utils import ParseExpressionError
from wc_rules import pattern
import unittest

class A(chem.Molecule):pass
class X(chem.Site):
    ph1 = core.BooleanAttribute(default=None)
    ph2 = core.BooleanAttribute(default=None)
class Y(chem.Site):
    ph = core.BooleanAttribute(default=None)
    v = core.IntegerAttribute(default=None)
@unittest.skip("")
class TestPattern(unittest.TestCase):

    def test_pattern_init(self):
        a1 = A(id='a1')
        x1 = X(id='x1')
        x2 = X(id='x2')
        a1.add_sites(x1,x2)

        p1 = pattern.Pattern('p1')
        self.assertTrue(len(p1)==0)
        p1.add_node(x1,recurse=False)
        self.assertTrue(len(p1)==1)
        del p1

        p1 = pattern.Pattern('p1',nodelist=[a1],recurse=True)
        self.assertTrue(len(p1)==3)
        del p1

        p1 = pattern.Pattern('p1',nodelist=[x1])
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

        p = pattern.Pattern('p').add_node(a,recurse=True)

        qdict = p.generate_queries()

        x = ['attr','rel','type','is_in','is_not_in']
        self.assertEqual(sorted(list(qdict.keys())), sorted(x))

        for idx in qdict['type']:
            node = p.get_node(idx)
            tuplist = qdict['type'][idx]
            for tup in tuplist:
                _class = tup[1]
                self.assertTrue(isinstance(node,_class))

        for idx in qdict['attr']:
            node = p.get_node(idx)
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

            node1 = p.get_node(idx1)
            node2 = p.get_node(idx2)
            self.assertTrue(node1 in node2.listget(attr2))
            self.assertTrue(node2 in node1.listget(attr1))

        for tup in qdict['is_in']:
            target_var = tup[1][0]
            source_pattern = tup[1][1][0]
            source_var = tup[1][1][1]

        for tup in qdict['is_not_in']:
            target_var = tup[1][0]
            source_pattern = tup[1][1][0]
            source_var = tup[1][1][1]

    def test_expressions(self):
        x1 = X('x1')
        p1 = pattern.Pattern('p1')  \
        .add_expression('!x1.ph1')     \
        .add_expression('x1.ph2 != False')

        #
        exprs1 = sorted(p1._expressions['bool_cmp'])
        tup1 = ('x1','ph1','!=',True)
        tup2 = ('x1','ph2','==',True)
        exprs2 = [tup1,tup2]
        self.assertEqual(exprs1,exprs2)

        with self.assertRaises(ParseExpressionError):
            p1.add_expression('x1')

        #
        y1 = Y('y1')
        p2= pattern.Pattern('p2')   \
        .add_expression('y1.v > 5')

        exprs1 = sorted(p2._expressions['num_cmp'])
        tup2 = ('y1','v','>',5)
        exprs2 = [tup2]
        self.assertEqual(exprs1,exprs2)

        #
        y1 = Y('y1')
        p2= pattern.Pattern('p2')   \
        .add_expression('y1 in p1.x')

        exprs1 = sorted(p2._expressions['is_in'])
        tup2 = (('y1',),'p1',('x',))
        exprs2 = [tup2]
        self.assertEqual(exprs1,exprs2)
