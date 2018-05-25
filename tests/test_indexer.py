"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""

from wc_rules.indexer import Indexer, Slicer
#from wc_rules.query import ClassQuery
from wc_rules.chem import Molecule
from wc_rules import utils
import itertools

import unittest

class A(Molecule):pass
class A1(A):pass
class A2(A):pass

class TestIndexer(unittest.TestCase):

    def test_slicer(self):
        # A positive slicer
        I = Slicer(default=False)
        self.assertTrue(len(I)==0)

        I.add_keys(['a','b'])
        self.assertTrue(len(I)==2)
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue('c' not in I)
        self.assertTrue(I['a'])
        self.assertTrue(I['b'])
        self.assertTrue(not I['c'])
        I.update({'a':False,'b':False})
        self.assertTrue(len(I)==0)

        # A negative slicer
        I = Slicer(default=True)
        self.assertTrue(len(I)==0)

        I.add_keys(['a','b'])
        self.assertTrue(len(I)==2)
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue('c' not in I)
        self.assertTrue(not I['a'])
        self.assertTrue(not I['b'])
        self.assertTrue(I['c'])
        I.update({'a':True,'b':True})
        self.assertTrue(len(I)==0)


    def test_slicer_AND(self):
        # positive & positive
        x1 = Slicer().update({'a':True,'b':True,'c':True})
        x2 = Slicer().update({'b':True,'c':True,'d':True})
        x = x1 & x2
        self.assertTrue(sorted(x.keys())==['b','c'])
        self.assertTrue(x['b'] and x['c'])
        self.assertTrue(not x['a'] and not x['d'])

        # negative & negative
        x1 = Slicer(default=True).update({'a':False,'b':False,'c':False})
        x2 = Slicer(default=True).update({'b':False,'c':False,'d':False})
        x = x1 & x2
        self.assertTrue(sorted(x.keys())==['a','b','c','d'])
        self.assertTrue(not any([x['a'],x['b'],x['c'],x['d']]))

        # positive & negative
        x1 = Slicer().update({'a':True,'b':True,'c':True})
        x2 = Slicer(default=True).update({'b':False,'c':False,'d':False})
        x = x1 & x2
        self.assertTrue(sorted(x.keys())==['a'])
        self.assertTrue(x['a'])
        self.assertTrue(not any([x['b'],x['c'],x['d']]))

        # negative & positive
        x = x2 & x1
        self.assertTrue(sorted(x.keys())==['a'])
        self.assertTrue(x['a'])
        self.assertTrue(not any([x['b'],x['c'],x['d']]))

    def test_slicer_OR(self):
        # positive & positive
        x1 = Slicer().update({'a':True,'b':True,'c':True})
        x2 = Slicer().update({'b':True,'c':True,'d':True})
        x = x1 | x2
        self.assertTrue(sorted(x.keys())==['a','b','c','d'])
        self.assertTrue(all([x['a'],x['b'],x['c'],x['d']]))

        # negative & negative
        x1 = Slicer(default=True).update({'a':False,'b':False,'c':False})
        x2 = Slicer(default=True).update({'b':False,'c':False,'d':False})
        x = x1 | x2
        self.assertTrue(sorted(x.keys())==['b','c'])
        self.assertTrue(all([x['a'],x['d']]))
        self.assertTrue(not any([x['b'],x['c']]))

        # positive & negative
        x1 = Slicer().update({'a':True,'b':True,'c':True})
        x2 = Slicer(default=True).update({'b':False,'c':False,'d':False})
        x = x1 | x2
        self.assertTrue(sorted(x.keys())==['d'])
        self.assertTrue(all([x['a'],x['b'],x['c']]))
        self.assertTrue(not x['d'])

        # negative & positive
        x = x2 & x1
        self.assertTrue(sorted(x.keys())==['a'])
        self.assertTrue(x['a'])
        self.assertTrue(not any([x['b'],x['c'],x['d']]))

    def test_slicer_NOT(self):
        x1 = Slicer().update({'a':True,'b':True,'c':True})
        x = ~x1
        self.assertTrue(sorted(x.keys())==['a','b','c'])
        self.assertTrue(not any([x['a'],x['b'],x['c']]))
        self.assertTrue(x['d'])
        x = ~~x1
        self.assertTrue(sorted(x.keys())==['a','b','c'])
        self.assertTrue(all([x['a'],x['b'],x['c']]))
        self.assertTrue(not x['d'])

    def test_indexing(self):
        I = Indexer()
        self.assertTrue(len(I)==len(I.value_cache)==0)

        I.update(dict(a=1,b=2))
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue(1 in I.value_cache and 2 in I.value_cache)
        self.assertTrue('a' in I.value_cache[1] and 'b' in I.value_cache[2])
        self.assertTrue(len(I)==2 and len(I.value_cache)==2)
        self.assertTrue(I.last_updated == set(['a','b']))
        I.flush()
        self.assertTrue(I.last_updated == set())

        I.update(dict(b=1))
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue(1 in I.value_cache and 2 not in I.value_cache)
        self.assertTrue('a' in I.value_cache[1] and 'b' in I.value_cache[1])
        self.assertTrue(len(I)==2 and len(I.value_cache)==1)
        self.assertTrue(I.last_updated == set(['b']))
        I.flush()
        self.assertTrue(I.last_updated == set())

        I.update(dict(a=3))
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue(1 in I.value_cache and 2 not in I.value_cache and 3 in I.value_cache)
        self.assertTrue('a' in I.value_cache[3] and 'b' in I.value_cache[1])
        self.assertTrue(len(I)==2 and len(I.value_cache)==2)
        self.assertTrue(I.last_updated == set(['a']))
        I.flush()
        self.assertTrue(I.last_updated == set())

        I.remove(['a'])
        self.assertTrue('a' not in I and 'b' in I)
        self.assertTrue(1 in I.value_cache and 2 not in I.value_cache and 3 not in I.value_cache)
        self.assertTrue('b' in I.value_cache[1])
        self.assertTrue(len(I)==1 and len(I.value_cache)==1)
        self.assertTrue(I.last_updated == set(['a']))
        I.flush()
        self.assertTrue(I.last_updated == set())

        I.remove(['b'])
        self.assertTrue(len(I)==len(I.value_cache)==0)
        self.assertTrue(I.last_updated == set(['b']))
        I.flush()
        self.assertTrue(I.last_updated == set())

    def test_indexer_types(self):
        # Boolean indexer
        I = Indexer(type='boolean').update({'x':True})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':7})

        # Numeric indexer
        I = Indexer(type='numeric').update({'x':1,'z':1.01})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':'ba'})

        # String indexer
        I = Indexer(type='string').update({'x':'x'})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':True})
            with self.assertRaises(utils.IndexerError):
                I.update({'y':1})

        # Arbitrary
        A = type('A',(),{})
        B = type('B',(),{})

        I = Indexer(type=A).update({'x':A()})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':B()})

        # Tuple of Arbitrary
        A1 = type('A1',(),{})
        I = Indexer(type=(A,A1)).update({'x':A(),'z':A1()})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':B()})

    def test_indexer_subset(self):
        I = Indexer().update(dict(a=1,b=2,c=3))
        self.assertTrue(sorted(I.last_updated)==['a','b','c'])

        I1 = I.subset(['a','b'])
        self.assertTrue('a' in I1 and 'b' in I1 and 'c' not in I1)
        self.assertTrue(sorted(I1.last_updated)==['a','b'])

        S = Slicer().add_keys(['a','b'])
        I2 = I.subset(S)
        self.assertTrue('a' in I2 and 'b' in I2 and 'c' not in I2)
        self.assertTrue(sorted(I2.last_updated)==['a','b'])

        I3 = I[S]
        self.assertTrue('a' in I3 and 'b' in I3 and 'c' not in I3)
        self.assertTrue(sorted(I3.last_updated)==['a','b'])

class TestClassQuery(unittest.TestCase):
    @unittest.skip
    def test_classquery(self):
        a1_01,a1_02 = A1(id='a1_01'), A1(id='a1_02')
        a2_01,a2_02 = A2(id='a2_01'), A2(id='a2_02')

        q_a = ClassQuery(A)
        q_a1 = ClassQuery(A1)
        q_a2 = ClassQuery(A2)
        instances = [a1_01,a1_02,a2_01,a2_02]
        queries = [q_a,q_a1,q_a2]

        for q in queries:
            id_list = [x.get_id() for x in instances if q.verify(x)]
            q.update(*id_list)

        q_a_keys = sorted(q_a.indexer.keys())
        q_a1_keys = sorted(q_a1.indexer.keys())
        q_a2_keys = sorted(q_a2.indexer.keys())

        self.assertEqual(q_a_keys,['a1_01','a1_02','a2_01','a2_02'])
        self.assertEqual(q_a1_keys,['a1_01','a1_02'])
        self.assertEqual(q_a2_keys,['a2_01','a2_02'])

        q_a_updates = sorted(q_a.indexer.last_updated)
        q_a1_updates = sorted(q_a1.indexer.last_updated)
        q_a2_updates = sorted(q_a2.indexer.last_updated)

        self.assertEqual(q_a_updates,['a1_01','a1_02','a2_01','a2_02'])
        self.assertEqual(q_a1_updates,['a1_01','a1_02'])
        self.assertEqual(q_a2_updates,['a2_01','a2_02'])

        for q in queries:
            q.indexer.flush()

        for q in queries:
            id_list = [x.get_id() for x in instances if q.verify(x)]
            q.remove(*id_list)

        self.assertEqual(len(q_a.indexer),0)
        self.assertEqual(len(q_a1.indexer),0)
        self.assertEqual(len(q_a2.indexer),0)
