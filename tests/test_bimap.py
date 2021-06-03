import unittest
from wc_rules.utils.collections import BiMap
	def test_mapping_sorting(self):
		# internal sorting 
		v = Mapping.create('zyx','cba')
		self.assertEqual(v.sort(),Mapping.create('xyz','abc'))
		self.assertEqual(v.sort('yxz'),Mapping.create('yxz','bac'))

		# external sorting
		# new behavior from bimap
		# sorting is done by order of sources, then order of targets
		v = sorted([Mapping.create(x) for x in ['yzx','zxy','xyz']])
		sources = [''.join(x.sources) for x in v]
		self.assertEqual(sources,['xyz','yzx','zxy'])

		# set behavior
		# note that all three mappings above are functionally identical, 
		# but have different orders of sources
		# set will treat each of them differently unless internally sorted
		self.assertEqual(len(set(v)),3)
		self.assertEqual(len(set([x.sort() for x in v])),1)



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

	def test_bimap_sorting(self):
		u = BiMap.create('zyx','zyx')
		v = BiMap.create('xyz','yzx')
		w = BiMap.create('xyz','zxy')
		x = [''.join(k.targets) for k in sorted([w,v,u])]
		self.assertEqual(x,['xyz','yzx','zxy'])
