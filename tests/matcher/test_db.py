from wc_rules.matcher.dbase import Database, DatabaseAlias, DatabaseSymmetric
from wc_rules.utils.collections import SimpleMapping
from wc_rules.graph.permutations import PermutationGroup, Permutation
from wc_rules.graph.examples import X,Y

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

		db.delete(dict(c=3))
		self.assertEqual(len(db),1)

		db.delete(dict(c=4))
		self.assertEqual(len(db),0)

class TestAlias(unittest.TestCase):

	def test_mapping(self):
		# xyz->abc * pqr->xyz = pqr->xyz
		m1 = SimpleMapping(zip('xyz','abc'))
		self.assertEqual(m1,dict(zip('xyz','abc')))
		self.assertEqual(m1.reverse,dict(zip('abc','xyz')))

		m2 = SimpleMapping(zip('pqr','xyz'))
		# testing multiply
		self.assertEqual(m1*m2,dict(zip('pqr','abc')))

		v = dict(zip('abc',range(3)))
		self.assertEqual(SimpleMapping(v)*m1,dict(zip('xyz',range(3))))
		self.assertEqual(SimpleMapping(v)*SimpleMapping(m1*m2),dict(zip('pqr',range(3))))


	def test_database_alias(self):
		db = Database(list('abc'))
		db.insert(dict(zip('abc',range(3))))

		alias1 = DatabaseAlias(db, dict(zip('xyz','abc')))
		alias2 = DatabaseAlias(alias1,dict(zip('pqr','xyz')))
		alias3 = DatabaseAlias(alias2,dict(zip('ijk','pqr')))
		
		self.assertEqual(alias1.target, db)
		self.assertEqual(alias2.target, db)
		self.assertEqual(alias3.target, db)
		
		self.assertEqual(alias1.mapping, dict(zip('xyz','abc')))
		self.assertEqual(alias2.mapping, dict(zip('pqr','abc')))
		self.assertEqual(alias3.mapping, dict(zip('ijk','abc')))

		# checking filtering
		record = db.filter(dict(a=0))[0]
		self.assertEqual(record,dict(zip('abc',range(3))))
		aliased1 = alias1.filter(dict(x=0))[0]
		aliased2 = alias2.filter(dict(p=0))[0]
		aliased3 = alias3.filter(dict(i=0))[0]
		self.assertEqual(aliased1,dict(zip('xyz',range(3))))
		self.assertEqual(aliased2,dict(zip('pqr',range(3))))
		self.assertEqual(aliased3,dict(zip('ijk',range(3))))

class TestDatabaseSymmetric(unittest.TestCase):

	def test_symmetric_insertion(self):
		p1 = Permutation.create(list('abc'),list('abc'))
		p2 = Permutation.create(list('abc'),list('acb'))
		G1 = PermutationGroup.create([p1,p2])

		db = DatabaseSymmetric(fields=list('abc'),symmetry_group=G1)
		self.assertEqual(db.symmetry_group,G1)
		self.assertEqual(len(db),0)

		x1,y1,y2 = X('x1'), Y('y1'), Y('y2')
		
		match1 = {'a':x1,'b':y1,'c':y2}
		db.insert(match1)
		self.assertEqual(len(db),1)
		
		# changing order of 'b' and 'c' should prevent insertion
		mapping = SimpleMapping(zip('abc','acb'))
		match2 = SimpleMapping(match1)*mapping
		self.assertEqual(match2,{'a':x1,'b':y2,'c':y1})
		db.insert(match2)
		# nothing happens
		self.assertEqual(len(db),1)

		# delete using match1 works
		db.delete(match1)
		self.assertEqual(len(db),0)
