import unittest
from wc_rules.utils.collections import BiMap, Mapping
from wc_rules.graph.permutations import Permutation, PermutationGroup

class TestMapping(unittest.TestCase):

	def test_mapping_basic(self):
		v = Mapping.create('xyz')
		self.assertEqual([v.get(x) for x in 'xyz'],list('xyz'))

		v = Mapping.create('xyz','abc')
		self.assertEqual([v.get(x) for x in 'xyz'],list('abc'))
		self.assertEqual(v, Mapping.create('xyz','abc'))
		self.assertEqual(v.sources,tuple('xyz'))
		self.assertEqual(v.targets,tuple('abc'))
		self.assertEqual(v._dict,dict(zip('xyz','abc')))
		self.assertEqual(v.reverse()._dict,dict(zip('abc','xyz')))
		self.assertEqual(v.restrict(['x','y'])._dict,dict(zip('xy','ab')))
		with self.assertRaises(AssertionError):
			Mapping.create('xyy','abc')._dict

	def test_mapping_mul(self):
		# Multiplying a match with a vertex relabeling
		v = Mapping.create('xyz','abc')
		m = Mapping.create('abc',range(3))
		self.assertEqual(m*v,Mapping.create('xyz',range(3)))

		# Multiplying with a rotation permutation
		v = Mapping.create('xyz','yzx')
		self.assertEqual(v*v, Mapping.create('xyz','zxy'))
		self.assertEqual(v*v*v, Mapping.create('xyz'))

	def test_mapping_sorting(self):
		# internal sorting 
		v = Mapping.create('zyx','cba')
		self.assertEqual(v.sort(),Mapping.create('xyz','abc'))
		self.assertEqual(v.sort(list('yxz')),Mapping.create('yxz','bac'))

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

class TestPermutation(unittest.TestCase):

	def test_cyclic_form(self):
		v = [
			Permutation.create('abc'), 
			Permutation.create('abc','acb'), 
			Permutation.create('abc','bac')
		]
		cyclic_forms = [x.cyclic_form(simple=True) for x in v]
		self.assertEqual(cyclic_forms,[
			'(a)(b)(c)',
			'(a)(b,c)',
			'(a,b)(c)'
		])

	def test_permutation_group_3triangle(self):

		with self.assertRaises(AssertionError):
			G = PermutationGroup.create([Permutation.create('abc','abd')])
			G.validate()

		# NOTE: the permutations here have been drawn by an 
		# imaginary implementation of ISMAGS algorithm on the 3triangle graph.
		G = PermutationGroup.create(
			[
				Permutation.create('abc','abc'),
				Permutation.create('abc','acb'),
				Permutation.create('abc','bac'),
			]
		)

		perms = G.expand()
		self.assertEqual(len(perms),6)
		permsources = set([''.join(x.sources) for x in perms])
		self.assertEqual(len(permsources),1)
		self.assertEqual(permsources.pop(),'abc')
		permtargets = [''.join(x.targets) for x in perms]
		self.assertEqual(permtargets,['abc', 'acb', 'bac', 'bca', 'cab', 'cba'])
		self.assertEqual(G.orbits,(tuple('abc'),))
		for x in 'abc':
			self.assertEqual(G.orbit(x),tuple('abc'))

		gendict = dict(zip(G.generators,range(len(G.generators))))
		subgroups = [[gendict[g] for g in Gsub.generators] for Gsub in G.iter_subgroups()]
		self.assertEqual(subgroups,[[0],[0,1],[0,2],[0,1,2]])

		
	def test_permutation_group_4square(self):

		# NOTE: the permutations here have been drawn by an 
		# imaginary implementation of ISMAGS algorithm on the 4square graph.
		
		G = PermutationGroup.create(
			[
				Permutation.create('abcd','abcd'),
				Permutation.create('abcd','adcb'),
				Permutation.create('abcd','badc'),
			]
		)

		perms = G.expand()
		self.assertEqual(len(perms),8)
		permsources = set([''.join(x.sources) for x in perms])
		self.assertEqual(len(permsources),1)
		self.assertEqual(permsources.pop(),'abcd')
		permtargets = [''.join(x.targets) for x in perms]
		self.assertEqual(permtargets,['abcd', 'adcb', 'badc', 'bcda', 'cbad', 'cdab', 'dabc', 'dcba'])
		self.assertEqual(G.orbits,(tuple('abcd'),))
		for x in 'abcd':
			self.assertEqual(G.orbit(x),tuple('abcd'))

		gendict = dict(zip(G.generators,range(len(G.generators))))
		subgroups = [[gendict[g] for g in Gsub.generators] for Gsub in G.iter_subgroups()]
		self.assertEqual(subgroups,[[0],[0,1],[0,2],[0,1,2]])



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
