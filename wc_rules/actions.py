
from collections import namedtuple
from .utils import print_as_tuple


### to create a token do XXXToken.new(*args)
### to create an action do XXXAction.new(*args)

######### TOKENS #############

class Token: 
	''' Refers to an object (node, attribute, edge) that may or may not exist '''

	def __eq__(self,other): return self.rep() == other.rep()
	def __ne__(self,other): return self.rep() != other.rep()
	def __lt__(self,other): return self.rep() < other.rep()
	def __le__(self,other): return self.rep() <= other.rep()
	def __gt__(self,other): return self.rep() > other.rep()
	def __ge__(self,other): return self.rep() >= other.rep()

	def __str__(self):
		return print_as_tuple(self.rep())

	@staticmethod
	def new():
		'''Checks class and attribute compatibilities and creates a new token. '''
		assert False, "Implement this!"
		return None

	def rep(self):
		''' Return a standard tuple representation of the token. '''
		assert False, "Implement this!"
		return None

	def transpose(self,idxmap=None):
		'''	Provide a method for mapping token objects to simulation instances '''
		assert False, "Implement this!"
		return None

class NodeToken(Token,namedtuple('NodeToken','cls id')):
	@staticmethod
	def new(_cls,id):
		return NodeToken(_cls,id)

	def rep(self):
		return tuple([self.cls.__name__,self.id])

	def transpose(self,idxmap=None):
		# assume idxmap preserves class relations
		if idxmap is None:
			return self
		return NodeToken(self._cls,idxmap[self.id])

class AttrToken(Token,namedtuple('AttrToken','cls id attr')):
	@staticmethod
	def new(_cls,id,attr):
		assert attr in _cls.Meta.local_attributes, "'" + attr + "' is not a valid attribute of " + str(_cls)
		return AttrToken(_cls,id,attr)

	def rep(self):
		return tuple([self.cls.__name__,self.id,self.attr])

	def transpose(self,idxmap=None):
		if idxmap is None:
			return self
		return AttrToken(self.cls,idxmap[self.id],self.attr)

class EdgeToken(Token,namedtuple('EdgeToken','port1 port2')):
	@staticmethod
	def new(_cls1,id1,attr1,_cls2,id2,attr2):
		p1 = AttrToken.new(_cls1,id1,attr1)
		p2 = AttrToken.new(_cls2,id2,attr2)
		local_attribute = _cls1.Meta.local_attributes[attr1]
		assert local_attribute.is_related and issubclass(_cls2,local_attribute.related_class), "'{0}'-'{1}' is not a valid pair of related attributes".format(attr1,attr2)
		return EdgeToken(p1,p2)

	def rep(self):
		return (self.port1.rep(), self.port2.rep())

	def transpose(self,idxmap=None):
		if idxmap is None:
			return self
		p1 = AttrToken(self.port1.cls,idxmap[self.port1.id],self.port1.attr)
		p2 = AttrToken(self.port2.cls,idxmap[self.port2.id],self.port2.attr)
		return EdgeToken(p1,p2)


########### ACTIONS ##############

class Action:
	''' Refers to an action that may be implemented on a token. '''

	def __init__(self,target,value=None,info=None):
		self.target = target
		# target can be NodeToken, AttrToken, EdgeToken, MatchToken
		self.value = value
		# value can be a literal or None
		self.info = info
		# info is additional info needed for rete nodes

	def rep(self):
		''' A standard tuple representation of the action. '''
		x = (self.__class__.__name__,str(self.target))
		if self.value is not None:
			x = x + (str(self.value),)
		if self.info is not None:
			x = x + (str(self.info),)
		return x

	def __str__(self):
		return print_as_tuple(self.rep())

	def execute(self,pool,idxmap=None):
		''' Transpose target with idxmap and execute the specified action. '''
		assert False, "Implement this!"
		return None

class InsertNode(Action):
	@staticmethod
	def new(_cls,id):
		return InsertNode(target=NodeToken.new(_cls,id))

	def execute(self,pool,idxmap=None):
		target = self.target.transpose(idxmap)
		pool.insert_item(target.cls(target.id))
		return self

class RemoveNode(Action):
	@staticmethod
	def new(_cls,id):
		return RemoveNode(target=NodeToken.new(_cls,id))

	def execute(self,pool,idxmap=None):
		target = self.target.transpose(idxmap)
		item = pool.fetch(target.id,target.cls)
		pool.remove_item(item)
		return self

class InsertEdge(Action):
	@staticmethod
	def new(_cls1,id1,attr1,_cls2,id2,attr2):
		return InsertEdge(target=EdgeToken.new(_cls1,id1,attr1,_cls2,id2,attr2))
	
	def execute(self,pool,idxmap=None):
		target = self.target.transpose(idxmap)
		items = [pool.fetch(x.id,x.cls) for x in target]
		attrs = [x.attr for x in target]
		items[0].add_edge(attrs[0],attrs[1],items[1])
		return self

class RemoveEdge(Action):
	@staticmethod
	def new(_cls1,id1,attr1,_cls2=None,id2=None,attr2=None):
		return RemoveEdge(target=EdgeToken.new(_cls1,id1,attr1,_cls2,id2,attr2))

	def execute(self,pool, idxmap=None):
		target = self.target.transpose(idxmap)
		items = [pool.fetch(x.id,x.cls) for x in target]
		attrs = [x.attr for x in target]
		items[0].remove_edge(attrs[0],attrs[1],items[1])
		return self


class SetAttr(Action):
	@staticmethod
	def new(_cls,id,attr,value):
		# TODO: check compatibility of value with attr
		return SetAttr(target=AttrToken.new(_cls,id,attr),value=value)

	def execute(self,pool,idxmap=None):
		target = self.target.transpose(idxmap)
		item = pool.fetch(target.id,target.cls)
		setattr(item,self.target.attr,self.value)
		return self


class CompositeAction(Action): pass

'''
def insert_match(somelist,info=None):
	return Action(action='insert',target=tuple(somelist),target_type='match',info=info)

def remove_match(somelist,info=None):
	return Action(action='remove',target=tuple(somelist),target_type='match',info=info)

def verify_match(somelist,info=None):
	return Action(action='verify',target=tuple(somelist),target_type='match',info=info)

def match_action(somelist,info=None,action='insert'):
	if action=='insert':
		return insert_match(somelist,info)
	if action=='remove':
		return remove_match(somelist,info)
	if action=='verify':
		return verify_match(somelist,info)
	return 

'''