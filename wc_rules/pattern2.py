from .indexer import DictLike
from .utils import generate_id,ValidateError,listmap, split_string, merge_dicts
from .canonical import canonical_label
from functools import partial
from .constraint import global_builtins, Constraint
from functools import wraps
from .entity import Entity
from pprint import pformat
from collections import ChainMap
#from attrdict import AttrDict

def helperfn(fn):
	fn._is_helperfn = True
	return fn

class GraphContainer(DictLike):

	def __init__(self,_list):
		super().__init__()
		assert len(set([x.id for x in _list]))==len(_list),"Duplicate ids detected on graph."
		assert all([isinstance(x.id,str) for x in _list]), "Graph node ids must be strings."
		for x in _list:
			self.add(x)

	def iternodes(self):
		for idx, node in self._dict.items():
			yield idx,node

	def iteredges(self):
		nodes_visited = set()
		for idx,node in self.iternodes():
			nodes_visited.add(node)
			for attr in node.get_nonempty_related_attributes():
				related_attr = node.get_related_name(attr)
				for related_node in node.listget(attr):
					if related_node not in nodes_visited:
						yield (node.id, attr), (related_node.id,related_attr)

	def iter_scalar_attrs(self):
		for idx,node in self.iternodes():
			for attr in node.get_nonempty_scalar_attributes():
				value = node.get(attr)
				yield idx, attr, value

	def get_canonical_label(self):
		return canonical_label(self)

class Parent:

	def __init__(self,canonical_form,variable_map):
		self.canonical_form = canonical_form
		self.variable_map = variable_map

	def get_namespace(self):
		d = dict()
		order = [x for y in self.canonical_form.partition for x in y]
		for i,source in enumerate(order):
			d[self.variable_map.get(source)]= self.canonical_form.classes[i]
		return d

	
class Pattern:

	def __init__(self,parent,helpers=dict(),constraints=[],assignments=dict()):
		self.parent = parent
		self.helpers = helpers
		self.constraints = constraints
		self.assignments = assignments

	def get_namespace(self):
		assignments = {x:y.code for x,y in self.assignments.items()}
		pspace = self.parent.get_namespace()
		intmax = max([int(x[1:]) for x in pspace if x[0]=='_'],default=0) + 1
		constraints = {'_{0}'.format(i+intmax):c.code for i,c in enumerate(self.constraints)}
		return merge_dicts([pspace, self.helpers, assignments, constraints])

	
	@classmethod
	def build(cls,parent,helpers={},constraints=''):
		err = "Argument for 'parent' keyword must be an entity node to recurse from or an existing pattern."
		assert isinstance(parent, (Entity,Pattern)), err
		
		constraint_strings = split_string(constraints)

		if isinstance(parent,Entity):
			d = GraphContainer(parent.get_connected())
			for idx, attr,value in d.iter_scalar_attrs():
				constraint_strings.append('{x}.{a}=={v}'.format(x=idx,a=attr,v=value))
				setattr(d[idx],attr,None)
			parent = Parent(*d.get_canonical_label())

		
		assert all([isinstance(x,cls) for x in helpers.values()]), "Helper variables must be assigned to other patterns."
		assert len(set(helpers.values())) == len(helpers), "The same helper pattern cannot be mapped to different helper variables."
						
		constraints,assignments = [],dict()
		for s in constraint_strings:
			c,var = Constraint.initialize(s)
			if var is not None:
				assignments[var] = c
			else:
				constraints.append(c)
			
		# checking consistent namespace
		r = set(parent.get_namespace())
		s = set(helpers.keys())
		t = set(assignments.keys())
		all_names = r|s|t

		assert len(all_names)==len(r) + len(s) + len(t), "Duplicate variables detected."
		for c in [*constraints,*assignments.values()]:
			assert set(c.keywords).issubset(all_names), "Unknown variables present in constraint '{0}'.".format(c.code)

		return Pattern(parent,helpers,constraints,assignments)

	def process_constraints(self,match=dict()):
		for var,c in self.assignments.items():
			match[var] = c.exec(match=match,helpers=self.helpers)
		outbool = all(c.exec(match,self.helpers) for c in self.constraints)
		return outbool, match

	@helperfn
	def count(self,**kwargs):
		return 0

	@helperfn
	def contains(self,**kwargs):
		return False






