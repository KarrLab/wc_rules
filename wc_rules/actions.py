
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

class NodeToken(Token,namedtuple('NodeToken','cls id')):
	@staticmethod
	def new(_cls,id):
		return NodeToken(_cls,id)

	def rep(self):
		return tuple([self.cls.__name__,self.id])

	def copy_with_idxmap(self,idxmap):
		return NodeToken(self._cls,idxmap[self.id])

class AttrToken(Token,namedtuple('AttrToken','cls id attr')):
	@staticmethod
	def new(_cls,id,attr):
		return AttrToken(_cls,id,attr)

	def rep(self):
		return tuple([self.cls.__name__,self.id,self.attr])

	def copy_with_idxmap(self,idxmap):
		return AttrToken(self.cls,idxmap[self.id],self.attr)

	
class EdgeToken(Token,namedtuple('EdgeToken','port1 port2')):
	@staticmethod
	def new(_cls1,id1,attr1,_cls2,id2,attr2):
		p1 = AttrToken(_cls1,id1,attr1)
		p2 = AttrToken(_cls2,id2,attr2)
		if p1 < p2:
			return EdgeToken(p1,p2)
		return EdgeToken(p2,p1)

	def rep(self):
		return (self.port1.rep(), self.port2.rep())

	def copy_with_idxmap(self,idxmap):
		p1 = AttrToken(self.port1.cls,idxmap[self.port1.id],self.port1.attr)
		p2 = AttrToken(self.port2.cls,idxmap[self.port2.id],self.port2.attr)
		return EdgeToken(p1,p2)


########### ACTIONS ##############

class Action:
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

	def execute(self,pool):
		assert False, "This method must be implemented for your action"
		return self


class InsertNode(Action):
	@staticmethod
	def new(_cls,id):
		return InsertNode(target=NodeToken.new(_cls,id))

	def copy_with_idxmap(self,idxmap):
		return InsertNode(target=self.target.copy_with_idxmap(idxmap))

	def execute(self,pool):
		pool.insert_item(self.target.cls(self.target.id))
		return self

	def compile(self,pool):
		return self

class RemoveNode(Action):
	@staticmethod
	def new(_cls,id):
		return RemoveNode(target=NodeToken.new(_cls,id))

	def copy_with_idxmap(self,idxmap):
		return RemoveNode(target=self.target.copy_with_idxmap(idxmap))

	def execute(self,pool):
		item = pool.fetch(target.id,target.cls)
		pool.remove_item(item)
		return self

	def compile(self,pool,idxmap):
		return self.copy_with_idxmap(idxmap)


class InsertEdge(Action):
	@staticmethod
	def new(_cls1,id1,attr1,_cls2,id2,attr2):
		return InsertEdge(target=EdgeToken.new(_cls1,id1,attr1,_cls2,id2,attr2))

	def copy_with_idxmap(self,idxmap):
		return InsertEdge(target=self.target.copy_with_idxmap(idxmap))

	def execute(self,pool):
		item1 = pool.fetch(self.target.port1.id,self.target.port1.cls)
		item2 = pool.fetch(self.target.port2.id,self.target.port2.cls)

		attr1str = self.target.port1.attr
		attr1 = getattr(item1,attr1str)
		attr2str = self.target.port2.attr
		attr2 = getattr(item2,attr2str)

		# TODO: test if inserting a new edge violates max_related conditions
		# for attributes on both sides of the edge
		
		if item1.__class__.Meta.local_attributes[attr1str].is_related_to_many:
			assert item2 not in attr1, "Edge already exists."
		else:
			assert attr1 is None, "Edge already exists."

		if item2.__class__.Meta.local_attributes[attr2str].is_related_to_many:
			assert item1 not in attr2, "Edge already exists."
		else:
			assert attr2 is None, "Edge already exists."

		if item1.__class__.Meta.local_attributes[attr1str].is_related_to_many:
			attr1.add(item2)
		else:
			setattr(item1,attr1str,item2)
		
		return self

	def compile(self,pool,idxmap):
		return self.copy_with_idxmap(idxmap)


class RemoveEdge(Action):
	@staticmethod
	def new(_cls1,id1,attr1,_cls2=None,id2=None,attr2=None):
		return RemoveEdge(target=EdgeToken.new(_cls1,id1,attr1,_cls2,id2,attr2))

	def copy_with_idxmap(self,idxmap):
		return RemoveEdge(target=self.target.copy_with_idxmap(idxmap))

	def execute(self,pool):
		item1 = pool.fetch(self.target.port1.id)
		item2 = pool.fetch(self.target.port2.id)

		attr1str = self.target.port1.attr
		attr1 = getattr(item1,attr1str)
		attr2str = self.target.port2.attr
		attr2 = getattr(item2,attr2str)
		

		if item1.__class__.Meta.local_attributes[attr1str].is_related_to_many:
			assert item2 in attr1, "Edge not found."
		else:
			assert attr1 is item2, "Edge not found."
		if item2.__class__.Meta.local_attributes[attr2str].is_related_to_many:
			assert item1 in attr2, "Edge not found."
		else:
			assert attr2 is item1, "Edge not found."
		
		if item1.__class__.Meta.local_attributes[attr1str].is_related_to_many:
			attr1.add(item2)
		else:
			setattr(item1,attr1str,None)
		
		return self

	def compile(self,pool,idxmap):
		return self.copy_with_idxmap(idxmap)


class SetAttr(Action):
	@staticmethod
	def new(_cls,id,attr,value):
		return SetAttr(target=AttrToken.new(_cls,id,attr),value=value)

	def copy_with_idxmap(self,idxmap):
		return SetAttr(target=self.target.copy_with_idxmap(idxmap),value=self.value)

	def execute(self,pool):
		item = pool.fetch(self.target.id)

		# TODO: check compatibility of value with attr
		setattr(item,self.target.attr,self.value)
		return self

	def compile(self,pool,idxmap):
		return self.copy_with_idxmap(idxmap)

class CompositeAction(Action): pass


		


#NodeToken = namedtuple('NodeToken',['cls','id'])
#EdgeToken = namedtuple('EdgeToken',['node1','attr1','attr2','node2'])
#AttrToken = namedtuple('AttrToken',['node','attr','value'])
#Action = namedtuple('Action',['action','target_type','target','info'])
'''
def insert_node(_cls,idx):
	target = NodeToken(cls=_cls,id=idx)
	return Action(action='insert',target=target,target_type='node',info=None)

def remove_node(_cls,idx):
	target = NodeToken(cls=_cls,id=idx)
	return Action(action='remove',target=target,target_type='node',info=None)

def edit_attr(_cls,idx,attr,value):
	node = NodeToken(cls=_cls,id=idx)
	target = AttrToken(node=node,attr=attr,value=value)
	return Action(action='edit',target=target,target_type='attr',info=None)

def node_action(_cls,idx,action='insert'):
	if action=='insert':
		return insert_node(_cls,idx)
	if action=='remove':
		return remove_node(_cls,idx)
	return 

def insert_edge(cls1,idx1,attr1,cls2,idx2,attr2):
	clsdict = {cls1.__name__:cls1,cls2.__name__:cls2}
	(attr1,clsname1,idx1),(attr2,clsname2,idx2) = sorted([(attr1,cls1.__name__,idx1),(attr2,cls2.__name__,idx2)])
	node1 = NodeToken(cls=clsdict[clsname1],id=idx1)
	node2 = NodeToken(cls=clsdict[clsname2],id=idx2)
	edge = EdgeToken(node1=node1,attr1=attr1,attr2=attr2,node2=node2)
	return Action(action='insert',target=edge,target_type='edge',info=None)

def remove_edge(cls1,idx1,attr1,cls2,idx2,attr2):
	clsdict = {cls1.__name__:cls1,cls2.__name__:cls2}
	(attr1,clsname1,idx1),(attr2,clsname2,idx2) = sorted([(attr1,cls1.__name__,idx1),(attr2,cls2.__name__,idx2)])
	node1 = NodeToken(cls=clsdict[clsname1],id=idx1)
	node2 = NodeToken(cls=clsdict[clsname2],id=idx2)
	edge = EdgeToken(node1=node1,attr1=attr1,attr2=attr2,node2=node2)
	return Action(action='remove',target=edge,target_type='edge',info=None)

def edge_action(cls1,idx1,attr1,cls2,idx2,attr2,action='insert'):
	if action=='insert':
		return insert_edge(cls1,idx1,attr1,cls2,idx2,attr2)
	if action=='remove':
		return remove_edge(cls1,idx1,attr1,cls2,idx2,attr2)
	return

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


class Action:
	def __init__(self,action,target_type,target,info=None):
		self.action = action
		self.target_type = target_type
		self.target = target
		self.info = info

	@staticmethod
	def insert_node(_cls,idx,info=None):
		target = NodeToken(cls=_cls,id=idx)
		return Action(action='insert',target=target,target_type='node',info=info)

	@staticmethod
	def remove_node(_cls,idx,info=None):
		target = NodeToken(cls=_cls,id=idx)
		return Action(action='remove',target=target,target_type='node',info=info)


	def __str__(self):
		def node_to_string(node):
			return ''.join(['(',node.cls.__name__,',',node.id,')'])

		def edge_to_string(edge):
			return ''.join(['(',node_to_string(edge.node1),'.',edge.attr1,'-',edge.attr2,'.',node_to_string(edge.node2),')'])

		def attr_to_string(attr):
			return ''.join(['(',node_to_string(attr.node),'.',attr.attr,':',str(attr.value),')'])

		def tuple_to_string(tup):
			strs = [str(x) for x in tup]
			return '(' + ','.join(strs) + ')'

	if isinstance(action.target,NodeToken):
		str1 = node_to_string(action.target)
	elif isinstance(action.target,EdgeToken):
		str1 = edge_to_string(action.target)
	elif isinstance(action.target,AttrToken):
		str1 = attr_to_string(action.target)
	else:
		str1 = tuple_to_string(action.target)
	return '<' + action.action + ' ' + action.target_type + ' ' + str1 + '>'

'''