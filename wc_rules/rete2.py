
from obj_model import core
from frozendict import frozendict
from .utils import ReteNetworkError,generate_id
import pandas as pd

class BiDirectionalMap(object):
	def __init__(self,some_dict):
		L = sorted(some_dict.items())
		self._forward = frozendict(some_dict)
		self._reverse = frozendict({y:x for x,y in some_dict.items()})

	def get(self,key,direction='forward'):
		if direction=='forward':
			return self._forward[key]
		elif direction=='reverse':
			return self._reverse[key]

class Keymap(BiDirectionalMap): pass

class Node(object): pass

class CheckType(Node):
	def __init__(self,_class):
		self._class = _class

	

'''
class Node(core.Model):
	downstream_pipes = core.OneToManyAttribute('Pipe',related_name = 'source')
	upstream_pipes = core.OneToManyAttribute('Pipe',related_name = 'target')

class Pipe(core.Model):
	def __init__(self,keydict,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.keymap = Keymap(keydict)

'''
