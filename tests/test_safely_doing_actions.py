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
	senders = ManyToManyAttribute('Person',related_name='receivers',max_related=2,max_related_rev=3)
	# one to many
	voters = OneToManyAttribute('Person',related_name='representative',max_related=2)
	# many to one
	leader = ManyToOneAttribute('Person',related_name='followers',max_related_rev=2)


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
		[john, jacob, jingle, hammer] = [self.john,self.jacob, self.jingle, self.hammer]

		jacob.safely_add_edge('representative',john)
		jingle.safely_add_edge('representative',john)

		self.assertEqual(jacob.representative,john)
		self.assertEqual(jingle.representative,john)
		self.assertTrue(jacob in john.voters and jingle in john.voters)

		with self.assertRaises(AssertionError):
			jacob.safely_add_edge('representative',john)

		with self.assertRaises(AssertionError):
			hammer.safely_add_edge('representative',john)

		with self.assertRaises(AssertionError):
			jacob.safely_add_edge('representative',hammer)

		john.safely_remove_edge('voters',jacob)
		john.safely_remove_edge('voters',jingle)

		with self.assertRaises(AssertionError):
			jacob.safely_remove_edge('representative',john)

		self.assertEqual(len(john.voters),0)
		self.assertEqual(jacob.representative,None)
		self.assertEqual(jingle.representative,None)

	def test_many_to_one(self):
		[john, jacob, jingle, hammer] = [self.john,self.jacob, self.jingle, self.hammer]

		john.safely_add_edge('followers',jacob)
		john.safely_add_edge('followers',jingle)

		self.assertEqual(jacob.leader,john)
		self.assertEqual(jingle.leader,john)
		self.assertTrue(jacob in john.followers and jingle in john.followers)

		with self.assertRaises(AssertionError):
			john.safely_add_edge('followers',jacob)

		with self.assertRaises(AssertionError):
			john.safely_add_edge('followers',hammer)

		with self.assertRaises(AssertionError):
			jacob.safely_add_edge('leader',hammer)

		jacob.safely_remove_edge('leader',john)
		jingle.safely_remove_edge('leader',john)

		with self.assertRaises(AssertionError):
			john.safely_remove_edge('followers',jacob)

	def test_many_to_many(self):
		[john, jacob, jingle, hammer, schmidt] = [self.john,self.jacob, self.jingle, self.hammer, self.schmidt]		
		senders = [john, jacob]
		receivers = [jingle, hammer, schmidt]

		for x in receivers:
			john.safely_add_edge('receivers',x)
		
		for x in receivers:
			x.safely_add_edge('senders',jacob)
			
		self.assertEqual(len(john.receivers),3)
		self.assertEqual(len(jacob.receivers),3)
		self.assertEqual(len(jingle.senders),2)
		self.assertEqual(len(hammer.senders),2)
		self.assertEqual(len(schmidt.senders),2)

		with self.assertRaises(AssertionError):
			jingle.safely_add_edge('senders',john)
		
		with self.assertRaises(AssertionError):
			jacob.safely_add_edge('receivers',jingle)

		for x in receivers:
			x.safely_remove_edge('senders',john)

		for x in receivers:
			jacob.safely_remove_edge('receivers',x)

		with self.assertRaises(AssertionError):
			john.safely_remove_edge('receivers',jingle)

		with self.assertRaises(AssertionError):
			jingle.safely_remove_edge('senders',jacob)

		for x in receivers:
			self.assertEqual(len(x.senders),0)
		for x in senders:
			self.assertEqual(len(x.receivers),0)


		