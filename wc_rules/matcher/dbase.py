from pydblite import Base
from ..utils.collections import SimpleMapping

def dict_overlap(d1,d2):
	return len(set(d1.items()) & set(d2.items())) > 0

def clean_record(r):
	return {k:v for k,v in r.items() if k not in ['__id__','__version__']}

class Database:

	def __init__(self,fields,**kwargs):
		self._db = Base(':memory:')
		self._db.create(*fields)
		
	@property
	def fields(self):
		return self._db.fields

	def insert(self,record):
		self._db.insert(**record)
		return self

	def filter(self,include_kwargs={},exclude_kwargs={}):
		records = self._db(**include_kwargs)
		if exclude_kwargs:	
			records = [x for x in records if dict_overlap(x,exclude_kwargs)]
		return [clean_record(x) for x in records]

	def delete(self,include_kwargs={},exclude_kwargs={}):
		records = self._db(**include_kwargs)
		if exclude_kwargs:	
			records = [x for x in records if dict_overlap(x,exclude_kwargs)]
		self._db.delete(records)
		return [clean_record(x) for x in records]

	def update(self,include_kwargs={},update_kwargs={}):
		records = self._db(**include_kwargs)
		for record in records:
			self._db.update(record,**update_kwargs)
		return self

	def filter_one(self,include_kwargs):
		records = self.filter(include_kwargs)
		if len(records)==1:
			return records[0]
		return None

	def __len__(self):
		return len(self._db)

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
		self.symmetry_aware = kwargs.pop('symmetry_aware',False)

	@property
	def fields(self):
		return self.mapping.keys()

	def forward_transform(self,match):
		return SimpleMapping(match)*self.mapping

	def reverse_transform(self,match):
		return SimpleMapping(match)*self.mapping.reverse

	def filter(self,include_kwargs={},exclude_kwargs={}):
		includes = self.reverse_transform(include_kwargs)
		excludes = self.reverse_transform(exclude_kwargs)
		records = self.target.filter(includes,excludes)
		rotated = [self.forward_transform(x) for x in records]
		return rotated


	