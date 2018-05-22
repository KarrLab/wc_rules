"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""

from wc_rules.indexer import Indexer
import unittest

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
