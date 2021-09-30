from pydblite import Base 

SEP = '   '

def initialize_database(fields):
	db =  Base(':memory:')
	db.create(*fields)
	return db

class Record:

	@staticmethod
	def itemize(r,ignore_keys=[]):
		return ((k,v) for k,v in r.items() if k not in ignore_keys and not k.startswith('__') and v)

	@staticmethod
	def retrieve(dbase,kwargs):
		return [dict(Record.itemize(r)) for r in dbase(**kwargs)]

	@staticmethod
	def retrieve_exactly(dbase,kwargs):
		records = Record.retrieve(dbase,kwargs)
		assert len(records) < 2
		record = records[0] if records else None
		return record

	@staticmethod
	def print(record,nsep=1,ignore_keys=[]):
		sep = SEP*nsep
		return '\n'.join([f'{sep}{k}: {v}' for k,v in Record.itemize(record,ignore_keys)])

	@staticmethod
	def insert(dbase,record):
		dbase.insert(**record)
		return

	@staticmethod
	def remove(dbase,record):
		dbase.delete(dbase(**record))
		return

	@staticmethod
	def retrieve_minus(dbase,include_kwargs,exclude_kwargs):
		exclude_ids = [x['__id__'] for x in dbase(**exclude_kwargs)]
		includes = [dict(Record.itemize(x)) for x in dbase(**include_kwargs) if x['__id__'] not in exclude_ids]
		return includes
