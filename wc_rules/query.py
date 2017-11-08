from obj_model import core
from wc_rules.base import BaseClass,DictClass
from wc_rules.entity import Entity
import wc_rules.graph_utils as g
from itertools import permutations,combinations

class NodeTypeQuery(DictClass):
	# Keys: Classes
	# Values: NodeQuery objects
	# Purpose is to look up a class, then find the NodeQuery objects to update
	# notation. new_cls, existing_cls
	def add_entry(self,new_cls,vec=set()):
		self.__setitem__(new_cls,vec)
		return self
	def add_to_entry(self,existing_cls,vec):
		vec2 = self.__getitem__(existing_cls)
		vec |= vec2
		self.add_entry(existing_cls,vec)
		return self
	def register_new_class(self,new_cls):
		vec = set()
		for existing_cls in self.keys():
			if issubclass(new_cls,existing_cls):
				vec |= self.__getitem__(existing_cls)
		self.add_entry(new_cls,vec)
		return self
	def register_new_nq(self,nq):
		self.register_new_class(nq.query.__class__)
		for existing_cls in self.keys():
			if issubclass(existing_cls,nq.query.__class__):
				self.add_to_entry(existing_cls,set([nq]))
		return self
	def __getitem__(self,key):
		if key not in self.keys():
			self.register_new_class(key)
		return super().__getitem__(key)

class NodeQuery(BaseClass):
	query = core.OneToOneAttribute(BaseClass,related_name='nq_query')
	matches = core.ManyToManyAttribute(BaseClass,related_name='nq_matches')

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		# This will be used by GraphQuery for propagating a match
		self.next_nq = dict()

	def verify_match(self,node):
		return g.node_compare(self.query,node)

	# Methods for dealing with a single match
	def add_match(self,node):
		self.matches.append(node)
		return self
	def remove_match(self,node):
		self.matches.discard(node)
		return self
	def update_match(self,node):
		# this is a method that ONLY checks verify_match
		if self.verify_match(node):
			if node not in self.matches:
				self.add_match(node)
		else:
			if node in self.matches:
				self.remove_match(node)
		return self

	# traversal functions define
	# how to use a current NQ1:N match and
	# a NQ1:NQ2 relation to get to the next
	# set of NQ2:N matches
	def get_traversal_functions(self,nq):
		node1 = self.query
		node2 = nq.query
		funcs =[]
		for attr in node1.attributes_that_contain(node2):
			apnd = node1.attribute_properties[attr]['append']
			if apnd:
				f = lambda x: getattr(x,attr)
			else:
				f = lambda x: [getattr(x,attr)]
			funcs.append(f)
		if len(funcs)>0:
			return funcs
		return None

class GraphMatch(DictClass):
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.keyorder = dict()
		self._signature = None
		self.new_nq = []
		return

	def orderedkeys(self):
		return list(sorted(self.keys(),key=lambda t:self.keyorder[t]))
	def nonekeys(self):
		return [x for x in self.orderedkeys() if self[x] is None]
	def not_nonekeys(self):
		return [x for x in self.orderedkeys() if self[x] is not None]
	def is_complete(self):
		return len(self.nonekeys())==0

	def signature(self,update=True):
		if self._signature is None or update is True:
			self._signature = self.to_string()
		return self._signature

	def __setitem__(self,key,value):
		super().__setitem__(key,value)
		self._signature = None

	def to_string(self):
		a = dict()
		for x in self.orderedkeys():
			if x in self.not_nonekeys():
				a[x.id] = self[x].id
			else:
				a[x.id] = None
		return a.__str__()

	def next_feasible_set_of_matches(self,next_nq):
		sets = []
		excludes = set(self.values())
		for current_nq in self.not_nonekeys():
			if next_nq in current_nq.next_nq:
				for func in current_nq.next_nq[next_nq]:
					target = self[current_nq]
					targetset = set(func(target)) - excludes
					sets.append(targetset)
		return list(set.intersection(*sets))

class GraphQuery(BaseClass):
	nodequeries = core.OneToManyAttribute(NodeQuery,related_name='graphquery')
	matches = core.OneToManyAttribute(GraphMatch,related_name='gq_matches')
	partial_matches = core.OneToManyAttribute(GraphMatch,related_name='gq_partial_matches')

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self._match_signatures = []
		self._partial_match_signatures = []

	def add_nodequery(self,nq):
		self.nodequeries.append(nq)
		return self

	def compile_traversal_functions(self):
		for x,y in permutations(self.nodequeries,2):
			d = x.get_traversal_functions(y)
			# d is either None or a list of funcs
			if d is not None:
				x.next_nq[y] = d
		return self

	def make_default_graphmatch(self,match=None,update_dict=None):
		gm = GraphMatch()
		for i,x in enumerate(self.nodequeries):
			gm.keyorder[x] = i
		if match is not None:
			for x,y in match.items():
				if x in gm.keyorder.keys():
					gm[x] = y
		if update_dict is not None:
			for x,y in update_dict.items():
				if x in gm.keyorder.keys():
					gm[x] = y
		for x in gm.keyorder.keys():
			if x not in gm.keys():
				gm[x] = None
		return gm

	def add_match(self,match):
		# add_match is intelligent w.r.t. whether match is partial or total
		iscomplete = match.is_complete()
		signature = match.signature()
		#print('trying to add match ',signature)
		if iscomplete and signature not in self._match_signatures:
			#print('added complete match ',signature)
			self.matches.append(match)
			self._match_signatures.append(signature)
		if not iscomplete and signature not in self._partial_match_signatures:
			#print('added incomplete match ',signature)
			self.partial_matches.append(match)
			self._partial_match_signatures.append(signature)
		return self

	def remove_match(self,match):
		# remove_match is intelligent w.r.t. whether match is partial or total
		iscomplete = match.is_complete()
		signature = match.signature()
		#print('trying to remove match ',signature)
		if iscomplete and signature in self._match_signatures:
			#print('removed complete match ',signature)
			self.matches.discard(match)
			self._match_signatures.remove(signature)
		if not iscomplete and signature in self._partial_match_signatures:
			#print('removed incomplete match ',signature)
			self.partial_matches.discard(match)
			self._partial_match_signatures.remove(signature)
		return self

	def update_for_new_nodequery_matches(self,nq_instance_tuplist=[]):
		# accepts a list of tuples of form (nq,node)
		# creates new partial graphmatches seeded with these tuples
		# calls process_partial_matches()
		pmatches = []
		for nq,node in nq_instance_tuplist:
			pmatch = self.make_default_graphmatch(update_dict={nq:node})
			self.add_match(pmatch)
		self.process_partial_matches()
		return self

	def pop_partial_match(self):
		x = self.partial_matches[-1]
		self.remove_match(x)
		return x

	def process_partial_matches(self):
		# This works as a LIFO stack
		while(len(self.partial_matches)>0):
			current_pmatch = self.pop_partial_match()
			#print('processing ',current_pmatch.to_string())
			pmatches = self.expand_partial_match(current_pmatch)
			for pmatch in pmatches:
				self.add_match(pmatch)
		return self

	def expand_partial_match(self,pmatch):
		# a graphmatch is 1-1 map between a set of nqs and a set of nq_matches
		# given a partial match, we first select_next_nq
		# then we select_next_nq_matches
		# one could potentially replace these with more efficient algorithms

		next_nq = self.select_next_nq(pmatch)
		if next_nq is None: return []
		valid_nodequery_matches = self.select_next_nq_matches(pmatch,next_nq)
		if len(valid_nodequery_matches)==0: return []
		elif len(valid_nodequery_matches)==1:
			# if there is only one possible nq_match, reuse the same pmatch
			pmatch[next_nq] = valid_nodequery_matches[0]
			return [pmatch]
		else:
			# if there are many possible nq_matches,
			# make a new copy for each possibility
			len2 = len(valid_nodequery_matches)
			pmatches = []
			for x in valid_nodequery_matches:
				pmatch2 = self.make_default_graphmatch(match=pmatch,update_dict={next_nq:x})
				pmatches.append(pmatch2)
			return pmatches
		return []

	def select_next_nq(self,pmatch):
		# Order nqs from nonekeys() depending on which one has
		# most connections to not_nonekeys()
		# return the one with the max
		n = dict()
		for x in pmatch.nonekeys():
			n[x] = len([z for z in pmatch.not_nonekeys() if x in z.next_nq])
		m = max(n.values())
		if m==0:
			return None
		return max(n,key=n.get)

	def select_next_nq_matches(self,pmatch,next_nq):
		candidates = pmatch.next_feasible_set_of_matches(next_nq)
		candidates2 = list(filter(lambda x: x in next_nq.matches,candidates))
		return candidates2




def main():
	pass


if __name__=='__main__':
	main()
