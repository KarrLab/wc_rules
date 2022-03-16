from .dbase import Database
from collections import deque

class ReteNodeState:
	
	def __init__(self,cache=None):
		self.incoming = deque()
		self.outgoing = deque()
		self.cache = cache

		# MANAGE CACHE CREATION OUTSIDE
		# in add_methods.py

	def cachelen(self):
		return len(self.cache) if self.cache is not None else None

	def length_characteristics(self):
		return [len(self.incoming),len(self.outgoing),self.cachelen()]