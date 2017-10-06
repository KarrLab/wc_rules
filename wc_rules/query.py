from obj_model import core
from wc_rules.base import BaseClass
from wc_rules.entity import Entity
import wc_rules.graph_utils as g

class NodeQuery(BaseClass):
	query = core.OneToOneAttribute(BaseClass,related_name='nq_query')
	matches = core.ManyToManyAttribute(BaseClass,related_name='nq_matches')
	
	def already_matched(self,node):
		return node in self.matches
	def remove_match(self,node):
		self.matches.remove(node)
		return self
	def add_match(self,node):
		self.matches.add(node)
		return self
	def verify_match(self,node):
		return g.node_compare(self.query,node)
	def update_node(self,node):
		if self.already_matched(node):
			if not self.verify_match(node):
				self.remove_match(node)
		else:
			if self.verify_match(node):
				self.add_match(node)
		return self

def main():
	pass

if __name__=='__main__':
	main()
