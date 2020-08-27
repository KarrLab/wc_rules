
from obj_model import core
from .attributes import *
import uuid
import random
from copy import deepcopy


class Rule:
	def __init__(self,id,reactants={},expressions=[],actions=[]):
		self.id = id
		self.reactants = reactants
		self.expression = expressions
		self.actions = actions
	
	def fire(self,pool,idxmap):
		for action in self.actions:
			action.execute(pool,idxmap)
		return self

	