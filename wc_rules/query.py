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

class GraphQuery(BaseClass):
	nodequeries = core.OneToManyAttribute(NodeQuery,related_name='graphquery')

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


def main():
	pass

if __name__=='__main__':
	main()
