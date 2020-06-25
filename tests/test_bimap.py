import unittest
from wc_rules.indexer import BiMap

class TestBiMap(unittest.TestCase):

	def test_bimap_basic(self):
		v = BiMap(dict(zip('xyz','abc')))
		self.assertEqual([v.get(x) for x in 'xyz'],list('abc'))
		v = BiMap.create('xyz','abc')
		self.assertEqual([v.get(x) for x in 'xyz'],list('abc'))
		self.assertEqual(v.sources,tuple('xyz'))
		self.assertEqual(v.targets,tuple('abc'))
		self.assertEqual(v._dict,dict(zip('xyz','abc')))

	def test_bimap_mul(self):
		v = BiMap.create('xyz','abc')
		m = BiMap.create('abc',range(3))
		m1 = m*v
		self.assertEqual(m1.sources,tuple('xyz'))
		self.assertEqual(m1.targets,tuple(range(3)))
		self.assertEqual(m1._dict,dict(zip('xyz',range(3))))

	def test_bimap_permut(self):
		v = BiMap.create('xyz','yzx')
		self.assertEqual(v._dict,dict(zip('xyz','yzx')))
		v1 = v*v
		self.assertEqual(v1._dict,dict(zip('xyz','zxy')))
		v2 = v*v*v
		self.assertEqual(v2, BiMap.create('xyz'))
