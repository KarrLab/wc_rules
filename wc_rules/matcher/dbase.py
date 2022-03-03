from pydblite import Base

def dict_overlap(d1,d2):
	return len(set(d1.items()) & set(d2.items())) > 0

def clean_record(r):
	return {k:v for k,v in r.items() if k not in ['__id__','__version__']}

class Database:

	def __init__(self,fields):
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
		
	def filter_one(self,include_kwargs):
		records = self.filter(include_kwargs)
		if len(records)==1:
			return records[0]
		return None

	def __len__(self):
		return len(self._db)