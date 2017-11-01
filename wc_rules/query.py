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

	# identifying relationships with another NodeQuery
	# will be used by GraphQuery
	def identify_relationships(self,nq):
		node1 = self.query
		node2 = nq.query
		# list of dicts with keys: attrname, append
		relations =[]
		for attr in node1.attributes_that_contain(node2):
			apnd = node1.attribute_properties[attr]['append']
			relations.append({'attrname':attr,'append':apnd})
		if len(relations)>0:
			return relations
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

	def signature(self):
		if self._signature is None:
			self._signature = self.to_string()
		return self._signature

	def to_string(self):
		a = dict()
		for x in self.orderedkeys():
			if x in self.not_nonekeys():
				a[x.id] = self[x].id
			else:
				a[x.id] = None
		return a.__str__()

class GraphQuery(BaseClass):
	nodequeries = core.OneToManyAttribute(NodeQuery,related_name='graphquery')
	matches = core.OneToManyAttribute(GraphMatch,related_name='gq_matches')
	partial_matches = core.OneToManyAttribute(GraphMatch,related_name='gq_partial_matches')

	def add_nodequery(self,nq):
		self.nodequeries.append(nq)
		return self

	def compile_nodequery_relations(self):
		for x,y in permutations(self.nodequeries,2):
			d = x.identify_relationships(y)
			# d is either None or a list of dicts {'attrname':str,'append':bool}
			if d is not None:
				x.next_nq[y] = d
		return self

	def make_default_graphmatch(self):
		gm = GraphMatch()
		for i,x in enumerate(self.nodequeries):
			gm[x] = None
			gm.keyorder[x] = i
		return gm

	def update_for_new_nodequery_matches(self,nq_instance_tuplist=[]):
		pmatches = []
		for nq,node in nq_instance_tuplist:
			pmatch = self.make_default_graphmatch()
			pmatch[nq] = node
			pmatches.append(pmatch)
		self.partial_matches.extend(pmatches)
		self.process_partial_matches()
		return self

	def process_partial_matches(self):
		while(len(self.partial_matches)>0):
			current_pmatch = self.partial_matches.pop()
			print('processing ',current_pmatch.to_string())
		return


def main():
	class A(BaseClass):
		b = core.OneToOneAttribute('B',related_name='a')
	class B(BaseClass):pass

	# query graph
	a1 = A(id='a1')
	b1 = B(id='b1')
	a1.b = b1
	gq = GraphQuery(id='gq')
	gq.add_nodequery( NodeQuery(query=a1,id='nq_a1') )
	gq.add_nodequery( NodeQuery(query=b1,id='nq_b1') )
	gq.compile_nodequery_relations()

	# instance graph
	a2 = A(id='a2')
	b2 = B(id='b2')
	a2.b = b2
	for nq in gq.nodequeries:
		for m in [a2,b2]:
			nq.update_match(m)

	nq_instance_tuplist = list(zip(gq.nodequeries,[a2,b2]))
	gq.update_for_new_nodequery_matches(nq_instance_tuplist)



if __name__=='__main__':
	main()
