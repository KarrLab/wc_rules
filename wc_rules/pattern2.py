from .indexer import GraphContainer
from .utils import generate_id,ValidateError,listmap, split_string, merge_dicts, no_overlaps
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

class Parent:
	# Wrapper class for canonical form to be used for parent patterns
	def __init__(self,canonical_form,variable_map):
		self.canonical_form = canonical_form
		self.variable_map = variable_map
		order = [x for y in self.canonical_form.partition for x in y]
		d = dict()
		for i,source in enumerate(order):
			d[variable_map.get(source)]= canonical_form.classes[i]
		self.namespace = d

	@classmethod
	def create(cls,g):
		# create a parent class from a graphcontainer
		return cls(*canonical_label(g))

	
class Pattern:

	def __init__(self,parent,helpers=dict(),constraints=dict(),namespace=dict()):
		self.parent = parent
		self.helpers = helpers
		self.constraints = constraints
		self.namespace = namespace
	'''
	def get_namespace(self):
		return merge_dicts([self.parent.get_namespace(), self.helpers, self.constraints])
	'''

	@classmethod
	def verify_helpers(cls,parent,helpers):
		err = "Helper variables must be assigned to Pattern instances."
		assert all([isinstance(x,cls) for x in helpers.values()]), err	
		err = 'In a pattern namespace, helper patterns must be assigned to variables uniquely'
		parent_helpers = parent.helpers.values() if isinstance(parent,Pattern) else []
		assert no_overlaps([parent_helpers,helpers.values()]), err
		

	@classmethod
	def verify_constraint_keywords(cls,namespace,constraints):
		for var,constraint in constraints.items():
			for keyword in constraint.keywords:
				err = "Variable '{v}' in '{c}' not found.".format(v=keyword,c=constraint.code)
				assert keyword in namespace,  err
		# TODO: check cycles:
		# as long as parent namespace was already consistent, it is sufficient
		# to just check cycles within constraints dict


	@classmethod
	def verify_namespace(cls,list_of_dicts):
		err = "Duplicate variables detected."
		assert no_overlaps(list_of_dicts), err
		

	@classmethod
	def build(cls,parent,helpers={},constraints=''):
		err = "Argument for 'parent' keyword must be an entity node to recurse from or an existing pattern."
		assert isinstance(parent, (Entity,Pattern)), err
		
		# building parent if Entity and updating constraint_strings
		cmax, constraint_strings = 0,[]
		# stripping parent graph of attrs and creating a Parent(CanonicalForm()) object
		if isinstance(parent,Entity):
			d,stripped_attrs = GraphContainer.build(parent.get_connected(),strip_attrs=True)
			parent = Parent.create(d)
			constraint_strings.extend(['{0}.{1}=={2}'.format(*x) for x in stripped_attrs])
		else:
			# parent is already a pattern, just update current_cmax
			cmax = len([x for x in parent.constraints if x[0]=='_'])

		# checking helpers
		cls.verify_helpers(parent,helpers)
		
		constraint_strings.extend(split_string(constraints))
		constraints = Constraint.initialize_strings(constraint_strings,cmax)
		
		# checking consistent namespace
		_dicts = [parent.namespace,helpers,{x:y.code for x,y in constraints.items()}]
		cls.verify_namespace(_dicts)
		namespace = merge_dicts(_dicts)
		
		# INCOMPLETE: checking if constraint keywords are compatible with namespace
		# and there are no cycles
		cls.verify_constraint_keywords(namespace,constraints)

		return Pattern(parent,helpers,constraints,namespace)

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






