"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""

from wc_rules.indexer import Indexer, Slicer
from wc_rules.indexer import BooleanIndexer, NumericIndexer, StringIndexer
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
        I = BooleanIndexer().update({'x':True})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':7})

        # Numeric indexer
        I = NumericIndexer().update({'x':1,'z':1.01})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':'ba'})

        # String indexer
        I = StringIndexer().update({'x':'x'})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':True})
            with self.assertRaises(utils.IndexerError):
                I.update({'y':1})

        # Arbitrary
        X = type('X',(),{})
        Y = type('Y',(),{})
        XIndexer = type('XIndexer',(Indexer,),dict(primitive_type=(X,)))

        I = XIndexer().update({'x':X()})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':Y()})

        # Tuple of Arbitrary
        X1 = type('X1',(),{})
        XIndexer = type('XIndexer',(Indexer,),dict(primitive_type=(X,X1,)))
        I = XIndexer().update({'x':X(),'z':X1()})
        with self.assertRaises(utils.IndexerError):
            I.update({'y':Y()})

    def test_indexer_subset(self):
        I = NumericIndexer().update(dict(a=1,b=2,c=3))
        self.assertTrue(sorted(I.last_updated)==['a','b','c'])

        I1 = I.subset(['a','b'])
        self.assertTrue('a' in I1 and 'b' in I1 and 'c' not in I1)
        self.assertTrue(sorted(I1.last_updated)==['a','b'])
        self.assertTrue(isinstance(I1,NumericIndexer))

        S = Slicer().add_keys(['a','b'])
        I2 = I.subset(S)
        self.assertTrue('a' in I2 and 'b' in I2 and 'c' not in I2)
        self.assertTrue(sorted(I2.last_updated)==['a','b'])
        self.assertTrue(isinstance(I2,NumericIndexer))

        I3 = I[S]
        self.assertTrue('a' in I3 and 'b' in I3 and 'c' not in I3)
        self.assertTrue(sorted(I3.last_updated)==['a','b'])
        self.assertTrue(isinstance(I3,NumericIndexer))

    def test_indexer_slice(self):
        I = NumericIndexer().update(dict(a=1,b=2,c=3,d=4))
        s = I.slice([1,2])
        self.assertTrue(s['a'] and s['b'] and not s['c'] and not s['d'])
        s = I.slice(lambda x: x<=3)
        self.assertTrue(s['a'] and s['b'] and s['c'] and not s['d'])
        s = I.slice()
        self.assertTrue(s['a'] and s['b'] and s['c'] and s['d'])

    def test_indexer_slice_subset(self):
        I1 = NumericIndexer().update(dict(a=1,b=2,c=3,d=4))
        I2 = StringIndexer().update(dict(a='p',b='q',c='r',d='s'))
        I3 = I2[I1.slice([1,2])]
        self.assertTrue('a' in I3 and 'b' in I3 and not 'c' in I3 and not 'd' in I3)
        self.assertTrue(I3['a']=='p' and I3['b']=='q')

    def test_indexer_eq_ne(self):
        I1 = NumericIndexer().update(dict(a=1,b=2,c=3,d=4))
        I2 = NumericIndexer().update(dict(a=1,b=2,c=3,d=4))
        x = I1 == I2
        y = I1 != I2
        for i in ['a','b','c','d']:
            self.assertTrue(x[i])
            self.assertTrue(not y[i])

        I3 = NumericIndexer().update(dict(a=1,b=2,c=4,d=5))
        x = I1 == I3
        y = I1 != I3
        for i in ['a','b']:
            self.assertTrue(x[i])
            self.assertTrue(not y[i])
        for i in ['c','d']:
            self.assertTrue(not x[i])
            self.assertTrue(y[i])

        I4 = StringIndexer().update(dict(a='p',b='q',c='r',d='s'))
        I5 = I4[I1==[1,2]]
        self.assertTrue(I5['a']=='p' and I5['b']=='q')
        self.assertTrue('c' not in I5 and 'd' not in I5)

        I6 = I4[I1!=[1,2]]
        self.assertTrue(I6['c']=='r' and I6['d']=='s')
        self.assertTrue('a' not in I6 and 'b' not in I6)
