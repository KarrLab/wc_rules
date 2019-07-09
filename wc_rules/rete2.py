
from obj_model import core
from .indexer import DictLike
from .base import BaseClass

from itertools import combinations
from collections import namedtuple
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
			
			# first, add check_type nodes
			for node in pattern:
				self.add_checktype_path(node.__class__)

			# then, add check_edge nodes
			for etuple in patdict['edges']:
				self.add_checkedge(etuple)
			
			# then, add check_attr nodes
			for atuple in patdict['attrs']:
				self.add_checkattr(atuple)
			
			# then, add merge nodes
			for mtuple in patdict['merges']:
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