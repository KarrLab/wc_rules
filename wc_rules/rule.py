
from obj_model import core
from .attributes import *
import uuid
import random
from copy import deepcopy


class Rule:
	def __init__(self,id,reactants={},actions=[]):
		self.id = id
		self.reactants = reactants
		self.actions = actions

	def add_reactant(self,alias,pattern):
		self.reactants[alias] = pattern
		return self

	
	def fire(self,pool,idxmap):
		for action in self.actions:
			action.execute(pool,idxmap)
		return self