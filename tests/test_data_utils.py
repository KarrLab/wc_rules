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

	def test_nested_dict(self):
		d = dict(dutil.NestedDict.iter_items(self.test_data))
		self.assertEqual(d,self.flat_data)

		d1 = dutil.NestedDict.compose(d)
		self.assertEqual(d1,self.test_data)

		d2 = dutil.NestedDict.simplify(d)
		self.assertEqual(d2,self.simplified_data)

		d3 = dutil.NestedDict.compose({'m.a':1}, {'m.b':1}, {'m.b':2})
		self.assertEqual(d3, {'m':{'a':1,'b':2}})

		d4 = dutil.NestedDict.compose({('m','a'):1}, {('m','b'):1}, {('m','b'):2})
		self.assertEqual(d4, {'m':{'a':1,'b':2}})


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
