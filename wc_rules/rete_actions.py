
from collections import namedtuple
from .utils import print_as_tuple
from .actions import Token

class MatchToken(Token,namedtuple('MatchToken','tuple')):
	@staticmethod
	def new(tup):
		return MatchToken(tup)

	def rep(self):
		return self.tuple

class ReteAction:
	''' Refers to an action that may be implemented on a token. '''

	action_type = None
	def __init__(self,target,value=None,info=None):
		self.target = target
		# target can be NodeToken, AttrToken, EdgeToken, MatchToken
		self.value = value
		# value can be a literal or None
		self.info = info
		# info is additional info needed for rete nodes

	def rep(self):
		x = (self.__class__.__name__,str(self.target))
		if self.value is not None:
			x = x + (str(self.value),)
		if self.info is not None:
			x = x + (str(self.info),)
		return x

	def __str__(self):
		return print_as_tuple(self.rep())

class InsertMatch(ReteAction):
	@staticmethod
	def new(tup):
		return InsertMatch(target=MatchToken.new(tup))

class RemoveMatch(ReteAction):
	@staticmethod
	def new(tup):
		return RemoveMatch(target=MatchToken.new(tup))

class VerifyMatch(ReteAction):
	@staticmethod
	def new(tup):
		return VerifyMatch(target=MatchToken.new(tup))