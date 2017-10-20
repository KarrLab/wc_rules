from obj_model import core
from wc_rules.base import BaseClass
from wc_rules.entity import Entity
import wc_rules.graph_utils as g

class NodeQuery(BaseClass):
	query = core.OneToOneAttribute(BaseClass,related_name='nq_query')
	# list of candidate matches
	# i.e., candiate.__class__ is compatible with query.__class__
	match_candidates = core.ManyToManyAttribute(BaseClass,related_name='nq_matches')

	# keys are node instances
	# The presence of a key indicates that it is a candidate match, i.e.,
	# values are booleans
	# value=True implies that a match exists
	# value=False implies that a match does not exist
	def __init__(self,**kwargs):
		super(NodeQuery,self).__init__(**kwargs)
		self.match_dict=dict()

	# Boolean methods used for verifying a match
	def already_matched(self,node):
		return node in self.match_candidates
	def verify_candidate_match(self,node):
		return isinstance(node,self.query.__class__)
	def verify_match(self,node):
		return g.node_compare(self.query,node)

	# updating match_dict
	def update_match_dict(self,node,remove=False):
		self.match_dict[node] = None
		if remove:
			del self.match_dict[node]
		else:
			self.match_dict[node] = self.verify_match(node)
		return self

	# Methods for dealing with a single match or match candidate
	def add_new_match_candidate(self,node):
		if self.verify_candidate_match(node):
			self.match_candidates.append(node)
			self.update_match_dict(node)
		return self
	def remove_existing_match_candidate(self,node):
		if self.already_matched(node):
			self.match_candidates.remove(node)
			self.update_match_dict(node,remove=True)
		return self
	def update_existing_match_candidate(self,node):
		self.update_match_dict(node)
		return self


if __name__=='__main__':
	main()
