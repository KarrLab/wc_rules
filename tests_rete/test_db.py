from wc_rules.matcher.dbase import Database, DatabaseAlias
from wc_rules.utils.collections import SimpleMapping

import unittest

class TestDatabase(unittest.TestCase):

	def test_db(self):

		db = Database(list('abc'))
		self.assertEqual(db.fields,list('abc'))
		self.assertEqual(len(db.filter(dict(a=1))),0)

		record = dict(a=1,b=2,c=3)
		db.insert(record)
		self.assertEqual(len(db),1)
		self.assertEqual(len(db.filter(dict(a=1))),1)
		self.assertEqual(db.filter_one(dict(a=1)),dict(a=1,b=2,c=3))

		record = dict(a=1,b=3,c=4)
		db.insert(record)
		self.assertEqual(len(db),2)
		self.assertEqual(len(db.filter(dict(a=1))),2)
		self.assertEqual(len(db.filter(dict(b=2))),1)

		records = db.delete(dict(c=3))
		self.assertEqual(len(records),1)
		self.assertEqual(len(db),1)

		records = db.delete(dict(c=4))
		self.assertEqual(len(records),1)
		self.assertEqual(len(db),0)

class TestAlias(unittest.TestCase):

	def test_mapping(self):

		m1 = SimpleMapping(zip('xyz','abc'))
		self.assertEqual(m1,dict(zip('xyz','abc')))
		self.assertEqual(m1.reverse,dict(zip('abc','xyz')))

		m2 = SimpleMapping(zip('pqr','xyz'))
		# testing multiply
		self.assertEqual(m1*m2,dict(zip('pqr','abc')))
		v = dict(zip('abc',range(3)))

		self.assertEqual(m1.premultiply(v),dict(zip('xyz',range(3))))
		self.assertEqual(SimpleMapping(m1*m2).premultiply(v),dict(zip('pqr',range(3))))


	def test_database_alias(self):
		db = Database(list('abc'))
		db.insert(dict(a=1,b=2,c=3))

		alias1 = DatabaseAlias(db, dict(zip('xyz','abc')))
		alias2 = DatabaseAlias(alias1,dict(zip('pqr','xyz')))
		alias3 = DatabaseAlias(alias2,dict(zip('ijk','pqr')))
		
		self.assertEqual(alias1.target, db)
		self.assertEqual(alias2.target, db)
		self.assertEqual(alias3.target, db)
		
		self.assertEqual(alias1.mapping, dict(zip('xyz','abc')))
		self.assertEqual(alias2.mapping, dict(zip('pqr','abc')))
		self.assertEqual(alias3.mapping, dict(zip('ijk','abc')))
