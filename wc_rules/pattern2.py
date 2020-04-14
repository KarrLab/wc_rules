from .indexer import DictLike
from .utils import generate_id,ValidateError
from functools import partial
from .expr_new import process_constraint_strings


class Pattern(DictLike):

	def __init__(self,idx,nodelist=[],recurse=True):
		super().__init__()
		self.id = idx
		self._constraints = []
		self._finalized = False
		for node in nodelist:
			self.add_node(node,recurse=recurse)
        
	def add_node(self,node):
		# always recurse through graph and add everything
		if node in self:
			return self
		self.add(node)	
		for new_node in node.listget_all_related():
			self.add_node(new_node) 
		return self

	def add_constraints(self,string_input):
		tree,deps = process_constraint_strings(string_input)
		print(tree)
		print(deps)

