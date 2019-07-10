
from obj_model import core
from .indexer import DictLike
from .base import BaseClass
from .entity import Entity
from . import gml

from itertools import combinations
from collections import namedtuple,defaultdict,deque

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
		# info holds additional info pertaining to the specific node
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


		

NodeToken = namedtuple('NodeToken',['cls','id'])
InsertNode = namedtuple('InsertNode',['node'])
RemoveNode = namedtuple('RemoveNode',['node'])
EditAttr = namedtuple('EditAttr',['node','attr','value','old_value'])
InsertEdge = namedtuple('InsertEdge',['node1','attr1','attr2','node2'])
RemoveEdge = namedtuple('RemoveEdge',['node1','attr1','attr2','node2'])