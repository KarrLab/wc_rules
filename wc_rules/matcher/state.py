from .dbase import Database
from collections import deque

class ReteNodeState:
	
	def __init__(self,cachetype=None,**kwargs):
		self.incoming = deque()
		self.outgoing = deque()
		self.cache = None

		if cachetype == 'database':
			self.cache = Database(
				fields=kwargs.pop('fields'),
				symmetry_group=kwargs.pop('symmetry_group',None),
				symmetry_aware=kwargs.pop('symmetry_aware',False)
			)
		if cachetype == 'deque':
			self.cache = deque()
		

	def cachelen(self):
		return len(self.cache) if self.cache is not None else None

	def length_characteristics(self):
		return [len(self.incoming),len(self.outgoing),self.cachelen()]