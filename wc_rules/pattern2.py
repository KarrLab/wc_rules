from .indexer import DictLike
from .utils import generate_id,ValidateError,listmap
from .canonical import *
from functools import partial
from .expr_new import process_constraint_string, serialize
from .dependency import DependencyCollector
from .constraint import global_builtins, Constraint
from functools import wraps
from .entity import Entity
from pprint import pformat
#from attrdict import AttrDict

def helperfn(fn):
	fn._is_helperfn = True
	return fn
		
class Pattern:

	def __init__(self,scaffold,helpers=dict(),constraints=''):
		self.scaffold = scaffold
		self.variables = scaffold.keys()
		
		self.helpers = dict()
		self.constraints = []
		
		self.add_helpers(helpers)
		self.add_constraints(constraints)

		self.simulation_node = None

	@classmethod
	def build(cls,graphnode,helpers={},constraints=[]):
		nodes,edges = graphnode.get_connected_nodes_and_edges()
		
	def final_match_variables(self):
		return self.variables + [c.assignment for c in self.constraints if c.assignment is not None]

	def add_helpers(self,_dict):
		for variable,pattern in _dict.items():
			err = 'Error adding helper: '
			assert variable not in self.final_match_variables(), err+'Variable {v} already exists in this pattern.'.format(v=variable)
			assert isinstance(pattern,Pattern), err+"'{p}' is not a pattern.".format(p=pattern)
			assert pattern not in self.helpers.values(), err+'Pattern added to variable {v} has already been added as a helper.'.format(v=variable)
			assert pattern is not self, err+'Cannot add a pattern as its own helper.'
			self.helpers[variable] = pattern
		return self

	def get_namespace(self,as_string=False,as_list=False):
		if as_string:
			return pformat(self.get_namespace())
		d= {'scaffold':self.scaffold.get_namespace(),
		'helpers':self.helpers,
		'declared_variables':self.declared_variables,
		'constraints':self.constraints
		}
		if as_list:
			v1 = d['scaffold'].get_namespace(as_list=True)
			v2 = d['helpers'].keys()
			v3 = [c.assignment for c in self.constraints if c.assignment is not None]
			return v1 + v2 + v3
		return d

	def add_constraints(self,string_input):
		strings = listmap(str.strip,string_input.split('\n'))
		for string in strings:
			if len(string)==0:
				continue
			tree,deps = process_constraint_string(string)
			constraint = Constraint.initialize(DependencyCollector(deps),serialize(tree))
			self.constraints.append(constraint)
		return self

	
	@helperfn
	def count(self,**kwargs):
		return 0

	@helperfn
	def contains(self,**kwargs):
		return False






