from wc_rules.base import BaseClass
from wc_rules.attributes import *
import unittest

class SomeClass(BaseClass):

	str_attr = StringAttribute()
	int_attr = IntegerAttribute(min=3,max=5)
	# float_attr = FloatAttribute(min=2.9,max=5.1)
	bool_attr = BooleanAttribute()

class TestSafelySettingAttributes(unittest.TestCase):

	def setUp(self):
		self.x = SomeClass()

	def test_id_attr(self):

		with self.assertRaises(AssertionError):
			self.x.safely_set_attr('id',1)

		self.x.safely_set_attr('id','x')
		self.assertEqual(self.x.id,'x')
		self.x.safely_set_attr('id',None)
		self.assertEqual(self.x.id,None)
		

	def test_str_attr(self):

		with self.assertRaises(AssertionError):
			self.x.safely_set_attr('str_attr',1)

		self.x.safely_set_attr('str_attr','some_string')
		self.assertEqual(self.x.str_attr,'some_string')

	def test_bool_attr(self):

		for val in [1.0,'1',2,1,0]:
			with self.assertRaises(AssertionError):
				self.x.safely_set_attr('bool_attr',val)

		for val in [True,False,None]:
			self.x.safely_set_attr('bool_attr',val)
			self.assertEqual(self.x.bool_attr,val)

	def test_int_attr(self):

		for val in [1.0,'1',2,6]:
			with self.assertRaises(AssertionError):
				self.x.safely_set_attr('int_attr',val)

		for val in [3,4,5,None]:
			self.x.safely_set_attr('int_attr',val)
			self.assertEqual(self.x.int_attr,val)

	@unittest.skip("Need to test later")
	def test_float_attr(self):

		for val in [1.0,'1',2,6]:
			with self.assertRaises(AssertionError):
				self.x.safely_set_attr('float_attr',val)

		for val in [3,4,5,None]:
			self.x.safely_set_attr('float_attr',val)
			self.assertEqual(self.x.float_attr,val)


