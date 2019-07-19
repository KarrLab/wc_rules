
from obj_model import core
from .indexer import DictLike
from .base import BaseClass
from .entity import Entity
from . import gml

from itertools import combinations,product
from collections import namedtuple,defaultdict,deque
import pydblite as db
import pprint
from functools import reduce


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

		self[etuple].info['token_length'] = 2

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
				h = [str(x) for x in range(0,node.info['token_length'])]
				node.cache = node.cache.create(*h)
		return self

	def print_caches(self):
		start_node = self[ClassTuple(cls=Entity)]
		str1 = ''
		for idx,node in enumerate(self.depth_first_search(start_node)):
			str1 += str(node) + '\n'
			if node.cache is None or len(node.cache)==0:
				str1 += '[]\n\n'
			else:
				str1 += '[\n'
				for r in node.cache:
					elems = [str(r[x]) for x in node.cache.fields]
					str1 += ','.join(elems) + '\n'
				str1 += ']\n\n'
		return str1

        
	def draw_as_gml(self):
		node_labels, node_categories, idx_dict = dict(),dict(),dict()
		edge_tuples = list()
		start_node = self[ClassTuple(cls=Entity)]
		for idx,node in enumerate(self.depth_first_search(start_node)):
			node_labels[idx] = str(node)[1:-1]
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
# here, 'action'='insert'/'remove'/'verify'/'edit'
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

def edit_attr(_cls,idx,attr,value,old_value):
	node = NodeToken(cls=_cls,id=idx)
	target = AttrToken(node=node,attr=attr,value=value,old_value=old_value)
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
		ret = ''
		if self.signature == 'check_type':
			ret =  self.id.cls.__name__
		if self.signature == 'check_edge':
			x1 = self.id.cls1.__name__
			x2 = self.id.attr1
			x3 = self.id.attr2
			x4 = self.id.cls2.__name__
			str1 = x1 + '.' + x2 + ' - ' + x4 + '.' + x3
			ret= str1
		if self.signature == 'check_attr':
			ret= self.id.cls.__name__ + '.' + self.id.attr
		if self.signature == 'merge':
			ret= ''
		if self.signature == 'pattern':
			ret= self.id
		ret = '{' + ret + '}'
		return ret

	def process_action(self,action,verbose=False):
		if self.signature=='check_type':
			self.check_type_behavior(action,verbose)
		elif self.signature=='check_edge':
			self.check_edge_behavior(action,verbose)
		elif self.signature=='check_attr':
			self.check_attr_behavior(action,verbose)
		elif self.signature=='merge':
			self.merge_behavior(action,verbose)
		return self

	def process_action_all_relevant_nodes(self,action,attr,verbose=False):
		for node in getattr(self,attr):
			node.process_action(action,verbose)
		return self

	# behavior 1: check_type
	# receive action, check type, pass to types, attrs, edges, lhs's, 
	
	def verbose_textgenerator(self,action,verb='check',condition=None):
		str1 = str(self)
		str2 = action_to_string(action)
		verb = verb + 'ing'
		if condition is not None:
			str3 = ': '+str(condition)
		else:
			str3 = ''
		return ' '.join([str1,verb,str2,str3])
	
	def verbose_textgenerator2(self,somelist,verb='insert',tab=True):
		if tab:
			str1 = "\t"
		str2 =  '(' + ','.join([str(x) for x in somelist]) + ')'
		prep = ''
		if verb=='insert':
			prep = 'into'
		elif verb=='remove':
			prep = 'from'
		return ' '.join([str1,verb,str2,prep,'cache'])

	def check_type_behavior(self,action,verbose=False):
		# assume internal type is check_type
		# first check if type matches
		class_to_check = get_classname(action.target)
		reference_class = self.id.cls
		condition = issubclass(class_to_check,reference_class)
		
		if verbose:
			print(self.verbose_textgenerator(action,'check',condition))
			
		# if so pass it on to downstream nodes
		# check_types, check_edges, check_attrs, and as_lhss
		if condition:
			for node in self.to_types:
				node.process_action(action,verbose=verbose)
			relevant_attrs = {'edge':'to_edges','attr':'to_attrs'}
			if action.target_type in relevant_attrs:
				self.process_action_all_relevant_nodes(action,relevant_attrs[action.target_type],verbose=verbose)
			if action.target_type == 'node' and len(self.as_lhs) > 0:
				new_action = match_action([action.target.id],info='lhs',action=action.action)
				self.process_action_all_relevant_nodes(new_action,'as_lhs',verbose=verbose)
		return self

	# behavior 2: check_edge
	# receive edge action, check types, 
	# store if necessary, pass to lhss and rhss

	def check_edge_behavior(self,action,verbose=False):
		# assume action.target is an edge
		# first check if edge matches
		edge = action.target
		condition = all([edge.attr1==self.id.attr1,edge.attr2==self.id.attr2,issubclass(edge.node1.cls,self.id.cls1),issubclass(edge.node2.cls,self.id.cls2)])
		#check_tuple = (edge.node1.cls,edge.attr1,edge.attr2,edge.node2.cls)
		#condition = check_tuple == (tuple(self.id))
		
		if verbose:
			print(self.verbose_textgenerator(action,'check',condition))
			
		# identify what to do
		insertions = []
		removals = []
		if condition and action.action=='insert':
			insertions = [[edge.node1.id,edge.node2.id]]
		if condition and action.action=='remove':
			removals = self.cache(node1=edge.node1.id,node2=edge.node2.id)

		def convert_to_tuple(record,fields):
			return tuple([record[x] for x in fields])
		
		# update internal caches
		if len(removals) > 0:
			self.cache.delete(removals)
			if verbose:
				for elem in removals:
					print(self.verbose_textgenerator2(convert_to_tuple(elem,self.cache.fields),'remove'))

		for elem in insertions:
			self.cache.insert(*elem)
			if verbose:
				print(self.verbose_textgenerator2(elem,'insert'))

		self.cache.commit()
		

		def double_if_symmetric(elemlist,symmetric=False):
			# this is to return every edge and its reverse
			# if the edge-conditions being checked for are symmetric
			elems = []
			if not symmetric:
				elems = elemlist
			else:
				for elem in elemlist:
					elems.append(elem)
					elems.append(list(reversed(elem)))
			return elems

		symmetric = (self.id.cls1,self.id.attr1)==(self.id.cls2,self.id.attr2)

		removals2 = [convert_to_tuple(x,self.cache.fields) for x in removals]
		
		for elem in double_if_symmetric(removals2,symmetric):
			for side in ['lhs','rhs']:
				new_action = remove_match(elem,info=side)
				self.process_action_all_relevant_nodes(new_action,'as_'+side,verbose=verbose)
				

		for elem in double_if_symmetric(insertions,symmetric):
			for side in ['lhs','rhs']:
				new_action = insert_match(elem,info=side)
				self.process_action_all_relevant_nodes(new_action,'as_'+side,verbose=verbose)
		
		return self


	### behavior 3: check_attr
	# receive attr action, check types
	# update internal caches, then pass it to relevant patterns

	def check_attr_behavior(self,action,verbose=False):
		# cache has attr = ['node','value','old_value']
		attrtoken = action.target
		assert attrtoken.value != attrtoken.old_value
		condition = issubclass(attrtoken.node.cls,self.id.cls) and attrtoken.attr == self.id.attr

		if verbose:
			print(self.verbose_textgenerator(action,'check',condition))
		
		insertion = None
		removal = None
		if condition:
			node = attrtoken.node.id
			value = attrtoken.value
			old_value = attrtoken.old_value
			current_elems = list(self.cache('node')==node)
			
			# checks
			# current token's old value is existing value already stored in cache
			# unless current token's old value is None, in which case, there shd be no
			# matching element in the cache

			assert (attrtoken.old_value is not None) == len(current_elems)
			
			if len(current_elems) == 1:
				assert current_elems[0]['value'] == attrtoken.old_value
				removal = current_elems[0]
			if value is not None:
				insertion = (attrtoken.node.id,value,old_value)
			if removal is not None:
				self.cache.delete(removal)
				if verbose:
					somelist = [removal[x] for x in ['node','value','old_value']]
					print(self.verbose_textgenerator2(somelist,verb='remove',tab=True))
			if insertion is not None:
				self.cache.insert(*insertion)
				if verbose:
					print(self.verbose_textgenerator2(insertion,verb='insert',tab=True))
			self.cache.commit()
		# forward to downstream patterns
		new_action = verify_match([node],info=self.id)
		self.process_action_all_relevant_nodes(new_action,'as_attrs',verbose)
		
		return self


	### behavior 3: merge
	# receive insert action from lhs, get matching elements from rhs and merge
	# also vice versa
	# send new merges downstream

	# receive remove action from lhs/rhs, filter cache, remove elements
	# send remove action downstream

	def merge_behavior(self,action,verbose=False):
		# this helps manage actions in both directions
		#print(action)
		side = dict()
		side_node = dict()
		if action.info=='lhs':
			side = {'first':'lhs','second':'rhs'}
			side_node = {'first':self.lhs, 'second':self.rhs}
			remap_dict = {'first':self.info['lhs_remap'],'second':self.info['rhs_remap']}
		elif action.info=='rhs':
			side = {'first':'rhs','second':'lhs'}
			side_node = {'first':self.rhs, 'second':self.lhs}
			remap_dict = {'first':self.info['rhs_remap'],'second':self.info['lhs_remap']}

		insertions = []
		removals = []
		# if it is an insert action, try to get a merge from the other side

		def reorder_element(match,remap,token_length,reverse=False):
			if reverse:
				remap = sorted([(y,x) for (x,y) in remap])
			elem = [None]*token_length
			for x,y in remap:
				elem[y] = match[x]
			return elem

		def satisfies_canonical_ordering(elem,symmetry_checks):
			for x,y in symmetry_checks:
				if elem[x] is not None and elem[y] is not None and elem[x] > elem[y]:
					return False
			return True

		def convert_to_tuple(record,fields):
			return tuple([record[x] for x in fields])

		def filter_cache(_cache,elem):
			fil = None
			for i,x in enumerate(elem):
				if x is not None:
					if fil is None:
						fil = (_cache(_cache.fields[i])==x)
					else:
						fil =  (_cache(_cache.fields[i])==x) & fil
			return list(fil)

		def interpolate(elem1,elem2):
			assert len(elem1) == len(elem2), "To interpolate, two matches must have same lengths"
			def choose(x,y):
				if x is None:
					return y
				return x
			return [choose(x,y) for x,y in zip(elem1,elem2)]
			
		if verbose:
			print(self.verbose_textgenerator(action,verb='process'))

		match = action.target
		elem = reorder_element(match,remap_dict['first'],self.info['token_length'])
		if not satisfies_canonical_ordering(elem,self.info['symmetry_checks']):
			if verbose:
				print('\t reject (' + ','.join(elem) + ') for symmetry reasons')
			return self
		
		#if action.action=='remove':
		#	elem = reorder_element(match,remap_dict['first'],self.info['token_length'])
		#	removals.extend(filter_cache(self.cache,elem))

		if action.action=='remove':
			side = action.info
			elem = reorder_element(match,self.info[side+'_remap'],self.info['token_length'])
			records = filter_cache(self.cache,elem)
			removals.extend(records)


		if action.action=='insert':
			if side_node['second'] is None:
				insertions.append(elem)
			else:
				filter_elem = reorder_element(elem,remap_dict['second'],side_node['second'].info['token_length'],reverse=True)
				elems2 = filter_cache(side_node['second'].cache,filter_elem)
				elems2 = [convert_to_tuple(x,side_node['second'].cache.fields) for x in elems2]
				elems2 = [reorder_element(x,remap_dict['second'],self.info['token_length']) for x in elems2]
				if len(elems2) > 0:
					new_elems = [interpolate(x,y) for x,y in product([elem],elems2)]
					for x in new_elems: 
						if satisfies_canonical_ordering(x,self.info['symmetry_checks']):
							insertions.append(x)
						elif verbose:
							print('\t reject (' + ','.join(x) + ') for symmetry reasons')

		self.cache.delete(removals)
		for elem in removals:
			if verbose:
				print(self.verbose_textgenerator2(convert_to_tuple(elem,self.cache.fields),'remove'))

		for elem in insertions:
			self.cache.insert(*elem)
			if verbose:
				print(self.verbose_textgenerator2(elem,'insert'))

		# propagate downstream
		for elem in removals:
			for side in ['lhs','rhs','scaffold']:
				new_action = remove_match(convert_to_tuple(elem,self.cache.fields),info=side)
				self.process_action_all_relevant_nodes(new_action,'as_'+side,verbose)
		for elem in insertions:
			for side in ['lhs','rhs','scaffold']:
				new_action = insert_match(elem,info=side)
				self.process_action_all_relevant_nodes(new_action,'as_'+side,verbose)
				

		self.cache.commit()

		return self

		
