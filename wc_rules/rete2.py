
from obj_model import core
from .indexer import DictLike
from .base import BaseClass
from .entity import Entity
from . import gml

from itertools import combinations
from collections import namedtuple,defaultdict,deque
import pydblite as db
import pprint


ClassTuple = namedtuple("ClassTuple",["cls"])

class ReteNet(DictLike):
	def __init__(self,pattern_collector):
		super().__init__()
		self.patterns = pattern_collector.patterns
		self.pattern_variables = pattern_collector.pattern_variables
		self.pattern_relations = pattern_collector.pattern_relations
		self.pattern_lengths = pattern_collector.pattern_lengths

		for pidx,pattern in self.patterns.items():
			patdict = pattern.build_rete_subset()
			self.pattern_variables[pidx] = patdict['mergepath'] + tuple(pattern.get_computed_variables())
			
			# note that we dont need all checktype nodes
			# only ones which lead into checkedge or checkattrs or merge nodes

			# then, add check_edge nodes
			for etuple in patdict['edges']:
				self.add_checktype_path(etuple.cls1)
				self.add_checkedge(etuple)
			
			# then, add check_attr nodes
			for atuple in patdict['attrs']:
				self.add_checktype_path(atuple.cls)
				self.add_checkattr(atuple)
			
			# then, add merge nodes
			for mtuple in patdict['merges']:
				if isinstance(mtuple.lhs,ClassTuple):
					self.add_checktype_path(mtuple.lhs.cls)
				self.add_merge(mtuple)

			# then, add pattern nodes
			ptuple = patdict['pattern_tuple']
			self.add_pattern(pattern,ptuple)


	def add_checktype_path(self,_class):
		ctuples = [ClassTuple(cls=x) for x in _class.__mro__ if x not in BaseClass.__mro__]
		for ctuple in ctuples:
			if ctuple not in self._dict:
				self.add(ReteNode(ctuple,'check_type'))

		for i in range(1,len(ctuples)):
			# i-1 th element is a subclass
			# i th element is a superclass
			# add outgoing edge from  i to i-1
			self[ctuples[i]].to_types.append(self[ctuples[i-1]])
		return self

	def add_checkedge(self,etuple):
		if etuple not in self._dict:
			self.add(ReteNode(etuple,'check_edge'))

		# etuple is cls1,attr1,attr2,cls2
		# add outgoing edge from ReteNode(cls1) to currentnode
		ctuple = ClassTuple(cls=etuple.cls1)
		self[ctuple].to_edges.append(self[etuple])
		return self

	def add_checkattr(self,atuple):
		if atuple not in self._dict:
			self.add(ReteNode(atuple,'check_attr'))

		# atuple is cls,attr
		# add outgoing edge from ReteNode(cls) to currentnode
		ctuple = ClassTuple(cls=atuple.cls)
		self[ctuple].to_attrs.append(self[atuple])
		return self

	def add_merge(self,mtuple):
		# mtuple has 'lhs','rhs','lhs_remap','rhs_remap',
		# 'token_length','symmetry_checks'
		if mtuple not in self._dict:
			self.add(ReteNode(mtuple,'merge'))
			self[mtuple].lhs = self[mtuple.lhs]
			self[mtuple].rhs = self._dict.get(mtuple.rhs,None)
			keys = ['lhs_remap','rhs_remap','token_length','symmetry_checks']
			infodict = mtuple._asdict()
			for key in keys:
				self[mtuple].info[key] = infodict[key]
		return self
			
	def add_pattern(self,pat,ptuple):
		assert pat.id not in self._dict

		# ptuple has 'scaffold','attrs',
		# scaffold_symmetry_breaks', 'internal_symmetries'
   
		self.add(ReteNode(pat.id,'pattern'))
		# add scaffold
		self[pat.id].scaffold = self[ptuple.scaffold]
		# add attrs
		for attr,indices in ptuple.attrs:
			self[pat.id].attrs.append(self[attr])

		self[pat.id].info['attr_remaps'] = dict(ptuple.attrs)
		self[pat.id].info['scaffold_symmetry_breaks'] = ptuple.scaffold_symmetry_breaks
		self[pat.id].info['internal_symmetries'] = ptuple.internal_symmetries
		self[pat.id].info['variables'] = self.pattern_variables[pat.id]
		self[pat.id].info['token_length'] = len(self.pattern_variables[pat.id])

		# add pattern orbits
		new_orbs = []
		for orb in pat._final_orbits:
			variables = self[pat.id].info['variables']
			new_orb = tuple(sorted([variables.index(i) for i in orb]))
			new_orbs.append(new_orb)
		self[pat.id].info['orbits'] = sorted(new_orbs)
		
		# add pattern relations
		pat_remaps = dict()
		rel_dict = self.pattern_relations.get(pat.id,dict())
		remap_tuples = []
		for pat2,varpairs in rel_dict.items():
			self[pat2].as_patterns.append(self[pat.id])
			for var2,var in varpairs:
				ind = self[pat.id].info['variables'].index(var)
				ind2 = self[pat2].info['variables'].index(var2)
				# pat2 is the incoming, pat is the current
				# remap_tuples are ordered (pat2.index,pat.index)
				# see explanation of remap_tuples in pattern.py
				remap_tuples.append([(ind2,ind)])
			pat_remaps[pat2] = sorted(remap_tuples)
		self[pat.id].info['pattern_remaps'] = pat_remaps

		return self


	def depth_first_search(self,start_node):
		def get_next_nodes(obj,visited):
			vec = []
			attrs = ['to_types','to_edges','to_attrs','as_lhs','as_rhs','as_scaffold','as_attrs','as_patterns'] 
			for attr in attrs:
				v = getattr(obj,attr)
				if not isinstance(v,list):
					v = [v]
				v = [x for x in v if x not in visited and x not in vec]
				#v = sorted(v,key = lambda x: list(x.id),reverse=True)
				vec = vec + v
			return vec

		visited = set()
		next_nodes = deque()  
		next_nodes.appendleft(start_node)
		while len(next_nodes) > 0:
		    current_node = next_nodes.popleft()
		    suc = get_next_nodes(current_node,visited)
		    next_nodes.extendleft(suc)
		    visited.add(current_node)
		    yield current_node

	def initialize_caches(self):
		signatures = ['check_edge','check_attr','merge','pattern']
		edge = ['node1','node2']
		attr = ['node','value','old_value']
		for node in self:
			if node.signature in signatures:
				node.cache = db.Base(':memory:')
			if node.signature=='check_edge':
				node.cache = node.cache.create(*edge)
			if node.signature=='check_attr':
				node.cache = node.cache.create(*attr)
			if node.signature in ['merge','pattern']:
				h = list(range(0,node.info['token_length']))
				node.cache = node.cache.create(*h)
		return self
        
	def draw_as_gml(self):
		node_labels, node_categories, idx_dict = dict(),dict(),dict()
		edge_tuples = list()
		start_node = self[ClassTuple(cls=Entity)]
		for idx,node in enumerate(self.depth_first_search(start_node)):
			node_labels[idx] = str(node)
			node_categories[idx] = node.signature
			idx_dict[node.id] = idx

		def outgoing_edges(node):
			attrs = ['to_types','to_edges','to_attrs','as_lhs','as_rhs','as_scaffold','as_attrs','as_patterns']
			edges = []
			for attr in attrs:
				v = getattr(node,attr)
				if not isinstance(v,list):
					v = [v]
				edges.extend(v)
			return edges

		for node in self:
			for node2 in outgoing_edges(node):
				edge_tuple = ( idx_dict[node.id], idx_dict[node2.id] )
				edge_tuples.append(edge_tuple)
		final_text = gml.generate_gml(node_labels,edge_tuples,node_categories)
		return final_text

	def process_action(self,action,verbose=False):
		ent = ClassTuple(cls=Entity)
		if verbose:
			print('Begin processing action ', action_to_string(action))
		self[ent].process_action(action,verbose)

		if verbose:
			print()
		return True

NodeToken = namedtuple('NodeToken',['cls','id'])
EdgeToken = namedtuple('EdgeToken',['node1','attr1','attr2','node2'])
AttrToken = namedtuple('AttrToken',['node','attr','value','old_value'])

Action = namedtuple('Action',['action','target_type','target','info'])
# here, 'action'='insert'/'remove'/'verify'
# 'target_type' = 'node','edge','attr','match'
# 'target' = NodeToken,EdgeToken,AttrToken,Tuple
# 'info' = additional info needed to process target (typically signature of sender)

def action_to_string(action):
	def node_to_string(node):
		return ''.join(['(',node.cls.__name__,',',node.id,')'])

	def edge_to_string(edge):
		return ''.join(['(',node_to_string(edge.node1),'.',edge.attr1,'-',edge.attr2,'.',node_to_string(edge.node2),')'])

	def attr_to_string(attr):
		return ''.join(['(',node_to_string(attr.node),'.',attr.attr,':',str(attr.old_value),'->',str(attr.value),')'])

	def tuple_to_string(tup):
		return '(' + ','.join(tup) + ')'

	if isinstance(action.target,NodeToken):
		str1 = node_to_string(action.target)
	elif isinstance(action.target,EdgeToken):
		str1 = edge_to_string(action.target)
	elif isinstance(action.target,AttrToken):
		str1 = attr_to_string(action.target)
	else:
		str1 = tuple_to_string(action.target)
	return '<' + action.action + ' ' + action.target_type + ' ' + str1 + '>'

def insert_node(_cls,idx):
	target = NodeToken(cls=_cls,id=idx)
	return Action(action='insert',target=target,target_type='node',info=None)

def remove_node(_cls,idx):
	target = NodeToken(cls=_cls,id=idx)
	return Action(action='remove',target=target,target_type='node',info=None)

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

def insert_match(somelist,info=None):
	return Action(action='insert',target=tuple(somelist),target_type='match',info=info)

def remove_match(somelist,info=None):
	return Action(action='remove',target=tuple(somelist),target_type='match',info=info)

def verify_match(somelist,info=None):
	return Action(action='verify',target=tuple(somelist),target_type='match',info=info)

# methods to process tokens
def get_classname(token):
	if isinstance(token,NodeToken):
		return token.cls
	if isinstance(token,EdgeToken):
		return token.node1.cls
	if isinstance(token,AttrToken):
		return token.node.cls
	assert False, "Something bad happened!"
	return


class ReteNode(core.Model):
	# outgoing edges to nodes that check types, edges and attrs
	to_types = core.OneToManyAttribute('ReteNode',related_name='as_type')
	to_edges = core.OneToManyAttribute('ReteNode',related_name='as_edge')
	to_attrs = core.OneToManyAttribute('ReteNode',related_name='as_attr')

	# outgoing edges to merge nodes
	as_lhs = core.OneToManyAttribute('ReteNode',related_name='lhs')
	as_rhs = core.OneToManyAttribute('ReteNode',related_name='rhs')

	# outgoing edges to pattern
	as_scaffold = core.OneToManyAttribute('ReteNode',related_name='scaffold')
	as_attrs = core.ManyToManyAttribute('ReteNode',related_name='attrs')
	as_patterns = core.ManyToManyAttribute('ReteNode',related_name='patterns')
	
	def __init__(self,idx,signature):
		# id is a special tuple
		# signature is the signal you send
		super().__init__()
		self.id = idx
		self.signature = signature
		self.cache = None
		self.info = dict()

	def __str__(self):
		if self.signature == 'check_type':
			return self.id.cls.__name__
		if self.signature == 'check_edge':
			x1 = self.id.cls1.__name__
			x2 = self.id.attr1
			x3 = self.id.attr2
			x4 = self.id.cls2.__name__
			str1 = x1 + '.' + x2 + ' - ' + x4 + '.' + x3
			return str1
		if self.signature == 'check_attr':
			return self.id.cls.__name__ + '.' + self.id.attr
		if self.signature == 'merge':
			return ''
		if self.signature == 'pattern':
			return self.id

	def process_action(self,action,verbose=False):
		if self.signature=='check_type':
			self.check_type_behavior(action,verbose)
		elif self.signature=='check_edge':
			self.check_edge_behavior(action,verbose)
		return self

	def process_action_all_relevant_nodes(self,action,attr,verbose=False):
		for node in getattr(self,attr):
			node.process_action(action,verbose)
		return self

	# behavior 1: check_type
	# receive action, check type, pass to types, attrs, edges, lhs's, 

	def check_type_behavior(self,action,verbose=False):
		# assume internal type is check_type
		# first check if type matches
		class_to_check = get_classname(action.target)
		reference_class = self.id.cls
		condition = issubclass(class_to_check,reference_class)
		
		if verbose:
			str1 = '{' + str(self) + '}'
			str2 = action_to_string(action)
			strs = [str1, 'checking',str2,':',str(condition)]
			print(' '.join(strs))

		# if so pass it on to downstream nodes
		# check_types, check_edges, check_attrs, and as_lhss
		if condition:
			for node in self.to_types:
				node.process_action(action,verbose=verbose)
			if action.target_type=='edge':
				self.process_action_all_relevant_nodes(action,'to_edges',verbose=verbose)
			if action.target_type=='attr':
				self.process_action_all_relevant_nodes(action,'to_atrrs',verbose=verbose)
			if action.target_type == 'node':
				if action.action=='insert':
					new_action = insert_new_match([action.target.id],info='lhs')
				if action.action=='remove':		
					new_action = remove_new_match([action.target.id],info='lhs')
				for node in self.as_lhs:
					node.process_action(new_action,verbose=verbose)	
		return self

	# behavior 2: check_edge
	# receive edge action, check types, 
	# store if necessary, pass to lhss and rhss

	def check_edge_behavior(self,action,verbose=False):
		# assume action.target is an edge
		# first check if edge matches
		edge = action.target
		check_tuple = (edge.node1.cls,edge.attr1,edge.attr2,edge.node2.cls)
		condition = check_tuple == (tuple(self.id))

		if verbose:
			str1 = '{' + str(self) + '}'
			str2 =  action_to_string(action)
			strs = [str1, 'checking',str2,':',str(condition)]
			print(' '.join(strs))

		# if so first update internal caches
		if condition and action.action=='insert':
			self.cache.insert(edge.node1.id,edge.node2.id)

			if verbose:
				str1 ='{' + str(self) + '}'
				str2 = ''.join(['(',edge.node1.id,',',edge.node2.id,')'])
				print('\t',str1, 'inserting', str2, 'into cache')

		if condition and action.action=='remove':
			recs = self.cache(node1=edge.node1.id,node2=edge.node2.id)
			self.cache.delete(recs)
			
			if verbose:
				for rec in recs:
					str1 ='{' + str(self) + '}'
					str2 = ''.join(['(',rec['node1'],',',rec['node2'],')'])
				print('\t',str1, 'removing', str2, 'from cache')
		
		
		# check if symmetric
		symmetric = (self.id.cls1,self.id.attr1)==(self.id.cls2,self.id.attr2)
		# then forward to any merge nodes
		
		if action.action=='insert':
			actions = [insert_match([action.target.node1.id,action.target.node2.id],info='lhs')]
			if symmetric:
				actions.append(insert_match([action.target.node1.id,action.target.node2.id],info='lhs'))
			for node in self.as_lhs:
				for action in actions:
					node.process_action(actions)

		if action.action=='remove':
			actions = [remove_match([action.target.node1.id,action.target.node2.id],info='rhs')]
			if symmetric:
				actions.append(remove_match([action.target.node1.id,action.target.node2.id],info='rhs'))
			for node in self.as_rhs:
				for action in actions:
					node.process_action(actions)

		return self
		