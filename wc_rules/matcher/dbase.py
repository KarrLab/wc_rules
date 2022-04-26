from pydblite import Base
from ..utils.collections import SimpleMapping
from sortedcontainers import SortedSet
import random

def dict_overlap(d1,d2):
	return len(set(d1.items()) & set(d2.items())) > 0

def clean_record(r):
	return {k:v for k,v in r.items() if k not in ['__id__','__version__']}

class Database:

	def __init__(self,fields,**kwargs):
		self._db = Base(':memory:')
		self._db.create(*fields)
		self._record_keys = SortedSet()
		
	@property
	def fields(self):
		return self._db.fields

	def insert(self,record):
		num = self._db.insert(**record)
		self._record_keys.add(num)
		return self

	def filter(self,kwargs={}):
		return [clean_record(x) for x in self._db(**kwargs)]

	def delete(self,kwargs={}):
		records = self._db(**kwargs)
		record_nums = [x['__id__'] for x in records]
		for num in record_nums:
			del self._db[num]
			self._record_keys.remove(num)
		return self

	def update(self,kwargs={},update_kwargs={}):
		records = self._db(**kwargs)
		for record in records:
			self._db.update(record,**update_kwargs)
		return self

	def filter_one(self,kwargs={}):
		records = self.filter(kwargs)
		if len(records)==1:
			return records[0]
		return None

	def __len__(self):
		return len(self._db)

	def count(self):
		return len(self)

	def sample(self):
		num = random.choice(self._record_keys)
		return clean_record(self._db[num])

	def contains(self,**kwargs):
		for x in self._db(**kwargs):
			return True
		return False

	def sum_over(self,variable):
		return sum([x[variable] for x in self.filter()])

class DatabaseSingleValue:

	def __init__(self,value=None):
		self.value = value

	def update(self,value):
		self.value = value

class DatabaseAlias:

	def __init__(self,target,mapping,**kwargs):
		

		'''
		Example: Parent database with fields a b c
		Child Alias with fields x y z
		Mapping stored in child: x->a, y->b, z->c
		Sending data downstream (foward)
		{a:1,b:2,c:3}*{x:a,y:b,z:3} = {x:1,y:2,z:3}
		Sending data request upstream (reverse)
		{x:1,y:2,z:3}*{x:a,y:b,z:3}^-1 = {a:1,b:2,c:3}
		'''
		
		if isinstance(target,DatabaseAlias):
			target, mapping = target.target, target.mapping*mapping

		self.target = target
		self.mapping = SimpleMapping(mapping)
		self.symmetry_group = kwargs.pop('symmetry_group',None)

	@property
	def fields(self):
		return self.mapping.keys()

	def forward_transform(self,match):
		return SimpleMapping(match)*self.mapping

	def reverse_transform(self,match):
		return SimpleMapping(match)*self.mapping.reverse

	def filter(self,kwargs={}):
		kwargs1 = self.reverse_transform(kwargs)
		records = self.target.filter(kwargs1)
		rotated = [self.forward_transform(x) for x in records]
		return rotated

	def count(self):
		return len(self.target)

	def __len__(self):
		return len(self.target)

	def sample(self):
		return self.forward_transform(self.target.sample())

	def contains(self,**kwargs):
		return self.target.contains(**self.reverse_transform(kwargs))
		

class DatabaseSymmetric(Database):

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.symmetry_group = kwargs.pop('symmetry_group',None)

	def insert(self,record):
		if self.symmetry_group.verify_symmetry_breaking(record):
			super().insert(record)
		return self

class DatabaseAliasSymmetric(DatabaseAlias):
	
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.symmetry_group = kwargs.pop('symmetry_group',None)

