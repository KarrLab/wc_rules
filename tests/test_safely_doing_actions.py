from wc_rules.base import BaseClass
from wc_rules.attributes import *
import unittest

class SomeClass(BaseClass):

	str_attr = StringAttribute()
	int_attr = IntegerAttribute(min=3,max=5)
	# float_attr = FloatAttribute(min=2.9,max=5.1)
	bool_attr = BooleanAttribute()

class Person(BaseClass):
	# one to one symmetric
	spouse = OneToOneAttribute('Person',related_name='spouse')
	# one to one asymmetric
	mentor = OneToOneAttribute('Person',related_name='mentee')
	# many to many symmetric
	friends = ManyToManyAttribute('Person',related_name='friends',max_related=2,max_related_rev=2)
	# many to many asymmetric
	senders = ManyToManyAttribute('Person',related_name='receivers',max_related=2,max_related_rev=2)
	# one to many
	representative = OneToManyAttribute('Person',related_name='voters',max_related=2)
	# many to one
	followers = ManyToOneAttribute('Person',related_name='leader',max_related_rev=2)


class TestSafelySettingAttributes(unittest.TestCase):

	def setUp(self):
		self.x = SomeClass()
		self.john = Person('john')
		self.jacob = Person('jacob')
		self.jingle = Person('jingle')
		self.hammer = Person('hammer')
		self.schmidt = Person('schmidt')

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

	# remember to test both directions
	def test_one_to_one_symmetric(self):
		[john, jacob, jingle] = [self.john,self.jacob, self.jingle]
		
		john.safely_add_edge('spouse',jacob)
		self.assertEqual(john.spouse,jacob)
		self.assertEqual(jacob.spouse,john)

		with self.assertRaises(AssertionError):
			john.safely_add_edge('spouse',jacob)

		with self.assertRaises(AssertionError):
			john.safely_add_edge('spouse',jingle)

		with self.assertRaises(AssertionError):
			jacob.safely_add_edge('spouse',jingle)

		jacob.safely_remove_edge('spouse',john)

		with self.assertRaises(AssertionError):
			john.safely_remove_edge('spouse',jacob)

		self.assertEqual(john.spouse,None)
		self.assertEqual(jacob.spouse,None)

	def test_many_to_many_symmetric(self):
		[john, jacob, jingle,hammer] = [self.john,self.jacob, self.jingle,self.hammer]

		john.safely_add_edge('friends',jacob)
		jacob.safely_add_edge('friends',jingle)
		jingle.safely_add_edge('friends',john)

		self.assertTrue(john in jacob.friends and john in jingle.friends)
		self.assertTrue(jacob in john.friends and jacob in jingle.friends)
		self.assertTrue(jingle in john.friends and jingle in jacob.friends)

		with self.assertRaises(AssertionError):
			john.safely_add_edge('friends',hammer)

		with self.assertRaises(AssertionError):
			hammer.safely_add_edge('friends',jacob)

		jacob.safely_remove_edge('friends',john)
		jacob.safely_remove_edge('friends',jingle)
		john.safely_remove_edge('friends',jingle)

		with self.assertRaises(AssertionError):
			john.safely_remove_edge('friends',jacob)

		self.assertEqual(john.friends,[])
		self.assertEqual(jacob.friends,[])
		self.assertEqual(jingle.friends,[])

	def test_one_to_one(self):
		[john, jacob, jingle] = [self.john,self.jacob, self.jingle]
		john.safely_add_edge('mentor',jacob)
		jacob.safely_add_edge('mentor',jingle)

		self.assertEqual(jacob.mentee,john)
		self.assertEqual(jingle.mentee,jacob)

		with self.assertRaises(AssertionError):
			jacob.safely_add_edge('mentee',john)

		with self.assertRaises(AssertionError):
			jacob.safely_add_edge('mentor',jingle)

		with self.assertRaises(AssertionError):
			jacob.safely_remove_edge('mentor',john)

		jacob.safely_remove_edge('mentee',john)
		jingle.safely_remove_edge('mentee',jacob)

		self.assertEqual(john.mentor,None)
		self.assertEqual(john.mentee,None)
		self.assertEqual(jacob.mentor,None)
		self.assertEqual(jacob.mentee,None)
		self.assertEqual(jacob.mentor,None)
		self.assertEqual(jacob.mentee,None)

	def test_one_to_many(self):
		pass

	def test_many_to_one(self):
		pass

	def test_many_to_many(self):
		pass





