from pydblite import Base 


def initialize_database(fields):
	db =  Base(':memory:')
	db.create(*fields)
	return db

class Record:

	@staticmethod
	def itemize(r):
		return ((k,v) for k,v in r.items() if not k.startswith('__') and v)

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
	def print(record,sep='    '):
		return '\n'.join([f'{sep}{k}: {v}' for k,v in Record.itemize(record)])

	@staticmethod
	def insert(dbase,record):
		dbase.insert(**record)
		return