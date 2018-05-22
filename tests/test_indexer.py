"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""

from wc_rules.indexer import Indexer, ClassQuery
from wc_rules.chem import Molecule
import itertools

import unittest

class A(Molecule):pass
class A1(A):pass
class A2(A):pass

class TestIndexer(unittest.TestCase):

    def test_indexer(self):
        I = Indexer()
        self.assertTrue(len(I)==len(I._values)==0)

        I.update(dict(a=1,b=2))
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue(1 in I._values and 2 in I._values)
        self.assertTrue('a' in I._values[1] and 'b' in I._values[2])
        self.assertTrue(len(I)==2 and len(I._values)==2)
        self.assertTrue(I.last_updated == set(['a','b']))
        I.flush()
        self.assertTrue(I.last_updated == set())

        I.update(dict(b=1))
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue(1 in I._values and 2 not in I._values)
        self.assertTrue('a' in I._values[1] and 'b' in I._values[1])
        self.assertTrue(len(I)==2 and len(I._values)==1)
        self.assertTrue(I.last_updated == set(['b']))
        I.flush()
        self.assertTrue(I.last_updated == set())

        I.update(dict(a=3))
        self.assertTrue('a' in I and 'b' in I)
        self.assertTrue(1 in I._values and 2 not in I._values and 3 in I._values)
        self.assertTrue('a' in I._values[3] and 'b' in I._values[1])
        self.assertTrue(len(I)==2 and len(I._values)==2)
        self.assertTrue(I.last_updated == set(['a']))
        I.flush()
        self.assertTrue(I.last_updated == set())

        I.remove('a')
        self.assertTrue('a' not in I and 'b' in I)
        self.assertTrue(1 in I._values and 2 not in I._values and 3 not in I._values)
        self.assertTrue('b' in I._values[1])
        self.assertTrue(len(I)==1 and len(I._values)==1)
        self.assertTrue(I.last_deleted == set(['a']))
        I.flush()
        self.assertTrue(I.last_deleted == set())

        I.remove('b')
        self.assertTrue(len(I)==len(I._values)==0)
        self.assertTrue(I.last_deleted == set(['b']))
        I.flush()
        self.assertTrue(I.last_deleted == set())

class TestClassQuery(unittest.TestCase):
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

        q_a_updates = sorted(q_a.indexer.last_deleted)
        q_a1_updates = sorted(q_a1.indexer.last_deleted)
        q_a2_updates = sorted(q_a2.indexer.last_deleted)

        self.assertEqual(q_a_updates,['a1_01','a1_02','a2_01','a2_02'])
        self.assertEqual(q_a1_updates,['a1_01','a1_02'])
        self.assertEqual(q_a2_updates,['a2_01','a2_02'])
