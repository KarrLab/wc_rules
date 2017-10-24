from obj_model import core
from wc_rules.base import BaseClass
from wc_rules.entity import Entity
import wc_rules.graph_utils as g

class NodeQuery(BaseClass):
	query = core.OneToOneAttribute(BaseClass,related_name='nq_query')
	matches = core.ManyToManyAttribute(BaseClass,related_name='nq_matches')

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

def main():
	class A(BaseClass):pass
	class B(BaseClass):pass
	x = A()
	a = [A(),A(),A()]
	b = [B(),B()]
	nq = NodeQuery(query=x)
	for item in a+b:
		nq.update_match(item)
	print(len(nq.matches))
	for item in a:
		nq.remove_match(item)
	print(len(nq.matches))
if __name__=='__main__':
	main()
