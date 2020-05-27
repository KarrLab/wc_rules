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



class Scaffold(DictLike):
	# scaffold, a graph with nodes and edges
	# nodes have all literal attrs set to None,except id attribute
	# namespace of scaffold = ids of nodes
	def __init__(self,node):
		assert isinstance(node,Entity), "Scaffold can only be initialized from some node of an entity graph."
		super().__init__()
		self.__add_node(node)
		self.properties = dict()
		x = canonize(self)
		self.simulation_node = None
		
	def __add_node(self,node):
		# always recurse through graph and add everything
		for attr in node.get_literal_attrs().keys():
			if attr == 'id':
				continue
			assert getattr(node,attr) is None, "Scaffold should not have attributes."
		assert node not in self or (node.id in self._dict and self[node.id] == node), "Id {0} duplicated".format(node.id)
	
		if node in self:
			return self
		self.add(node)	
		for new_node in node.listget_all_related():
			self.__add_node(new_node)
		return self

	def get_namespace(self,as_string=False,as_list=False):
		if as_string:
			return pformat(self.get_namespace())
		if as_list:
			return self.keys()
		return {x.id:x.__class__ for i,x in self._dict.items()}

	def compute_orbits(self):
		self.properties


def helperfn(fn):
	fn._is_helperfn = True
	return fn
		
class Pattern:

	def __init__(self,scaffold,helpers=dict(),constraints=''):
		assert isinstance(scaffold,Scaffold), "Scaffold keyword argument must be a scaffold."
		assert isinstance(helpers,dict), "Helpers keyword argument must be a dict."
		assert isinstance(constraints,str), "Constraints keyword argument must be a str."
		self.scaffold = scaffold
		self.variables = scaffold.keys()
		
		self.helpers = dict()
		self.constraints = []
		
		self.add_helpers(helpers)
		self.add_constraints(constraints)

		self.simulation_node = None

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






