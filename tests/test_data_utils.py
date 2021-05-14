import wc_rules.utils.data as dutil

import unittest

class TestDataUtils(unittest.TestCase):

	def setUp(self):
		self.test_data = {
		'x': 
			{
			'm':{'a':1,'b':2,},
			'n':{'b':3,'c':4,},
			},
		'y': {'a':5,'b':6,},
		'z': 7,
		}
		self.simplified_data = {
		'x.m.a': 1,
		'x.m.b': 2,
		'x.n.b': 3,
		'x.n.c': 4,
		'y.a': 5,
		'y.b': 6,
		'z': 7,
		}
		self.flat_data = {
		('x','m','a'): 1,
		('x','m','b'): 2,
		('x','n','b'): 3,
		('x','n','c'): 4,
		('y','a'): 5,
		('y','b'): 6,
		('z',): 7,
		}
		self.piece1 = {
		'x.m.a': 1,
		'x.m.b': 2,
		'x.n.b': 3,
		'x.n.c': 5,
		}
		self.piece2 = {
		('x','n','c'): 4,
		('y','a'): 5,
		('y','b'): 6,
		('z',): 7,
		}

	def test_nested_dict(self):
		# flattening nested data
		d1 = dict(dutil.NestedDict.iter_items(self.test_data))
		self.assertEqual(d1,self.flat_data)
		d2 = dict(dutil.NestedDict.iter_items(self.test_data,mode='str'))
		self.assertEqual(d2,self.simplified_data)

		# nesting flat data
		d3 = dutil.NestedDict.compose(*self.flat_data.items())
		self.assertEqual(d3,self.test_data)
		d4= dutil.NestedDict.compose(*self.simplified_data.items())
		self.assertEqual(d4,self.test_data)

		# combining overlapping pieces using compose and join
		d5 = dutil.NestedDict.compose(*self.piece1.items(),*self.piece2.items())
		self.assertEqual(d5,self.test_data)	
		d6 = dutil.NestedDict.join(
			dutil.NestedDict.compose(*self.piece1.items()),
			dutil.NestedDict.compose(*self.piece2.items())
			)
		self.assertEqual(d6,self.test_data)

		# get and set
		with self.assertRaises(KeyError):
			dutil.NestedDict.get(self.test_data,'x.n.k')
		self.assertEqual(dutil.NestedDict.get(self.test_data,'x.n.c'),4)
		self.assertEqual(dutil.NestedDict.get(self.test_data,('x','n','c')),4)
		dutil.NestedDict.set(self.test_data,'x.n.c',5)
		self.assertEqual(dutil.NestedDict.get(self.test_data,('x','n','c')),5)
		dutil.NestedDict.set(self.test_data,'x.n.k.d',5)
		self.assertEqual(dutil.NestedDict.get(self.test_data,('x','n','k')),{'d':5})
		

	def test_roundtrip(self):
		utils = [
			dutil.YAMLUtil,
			dutil.JSONUtil,
			dutil.PLISTUtil,
			dutil.JSONUtil
		]
		for util in utils:
			roundtrip_data = util.read(util.write(self.test_data))
			self.assertEqual(self.test_data,roundtrip_data)
