
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
		concrete_actions = []
		for action in self.actions:
			act = action.copy_with_idxmap(idxmap)
			concrete_actions.append(act)

		for act in concrete_actions:
			act.execute(pool)
		return self
