from .indexer import GraphContainer,DictLike
from .utils import generate_id,ValidateError,listmap, split_string, merge_dicts, no_overlaps, invert_dict
from .canonical import canonical_label
from .canonical_expr import canonical_expression_ordering
from functools import partial
from .executable_expr import ExecutableExpression, Constraint, Computation
from functools import wraps
from .entity import Entity
from pprint import pformat
from collections import ChainMap, Counter, deque
from .utils import check_cycle, merge_lists

#from attrdict import AttrDict

def helperfn(fn):
	fn._is_helperfn = True
	return fn

class ParentWrapper:
	'''
		Wrapper class adding "parent behavior" to canonically labeled graphs.
		Should be wrapped around objects intended to be parents to patterns.
		Must have a 
			source: the object that is the parent
			variable_map: a map between the variables of the parent and the child
			partition: conversion of the partition attribute of the parent using variable_map
			leaders: conversion of the leaders attributue of the parent using variable_map
			namespace: conversion of the parents
	'''

	def __init__(self,g):
		source,vmap = canonical_label(g)
		self.source = source
		self.variable_map = vmap
		self.partition = vmap.replace(source.partition)
		self.leaders = vmap.replace(source.leaders)
		self.namespace = {y:source.namespace[x] for x,y in vmap.items()}


class PatternArchetype:

	def __init__(self,parent=None,helpers=dict(),constraints=dict(),namespace=dict(),partition=tuple(),leaders=tuple()):
		self.parent = parent
		self.helpers = helpers
		self.constraints = constraints
		self.namespace = namespace
		self.partition = partition
		self.leaders = leaders


	@classmethod
	def build(cls,parent=GraphContainer(),helpers={},constraints=''):

		def make_constraint_strings(attrs):
			return ['{0}.{1}=={2}'.format(idx,attr,attrs[idx][attr]) for idx in attrs for attr in attrs[idx]]

		err = "Argument for 'parent' keyword must be a Pattern or a GraphContainer holding a connected graph."
		
		# Setting up parent
		assert isinstance(parent, (GraphContainer,Pattern)), err
		cmax, constraint_strings = 0,[]
		if isinstance(parent,GraphContainer):
			parent.validate_connected()
			g, stripped_attrs = parent.duplicate().strip_attrs()
			parent = ParentWrapper(g)
			constraint_strings.extend(make_constraint_strings(stripped_attrs))
		elif isinstance(parent,Pattern):
			cmax = len([x for x in parent.constraints if x[0]=='_'])
		
		# Setting up constraints
		constraint_strings.extend(split_string(constraints))
		constraints = ExecutableExpression.initialize_from_strings(constraint_strings,[Constraint,Computation],cmax)

		# Setting up helpers


		namespace,errs = verify_and_compile_namespace(parent,helpers,constraints)
		assert len(errs)==0, "Errors in namespace:\n{0}".format('\n'.join(errs))

		seed = parent.partition
		partition, leaders = canonical_expression_ordering(seed,namespace,constraints)
		#print(partition,leaders)
		return Pattern(parent,helpers,constraints,namespace,partition,leaders)
	

def verify_and_compile_namespace(parent,helpers,constraints):
	errs = []

	varcount = Counter()
	for d in [parent.namespace,helpers,constraints]:
		varcount.update(d.keys())
	for var in varcount:
		if varcount[var]>1:
			errs.append("Variable {0} assigned multiple times.".format(var))
	
	parent_helpers = parent.helpers if hasattr(parent,'helpers') else dict()
	inv_helpers = invert_dict(merge_dicts([parent_helpers,helpers]))
	for h,v in inv_helpers.items():
		if not isinstance(h,PatternArchetype):
			errs.append("Helper variable '{0}' must be assigned to a PatternArchetype instance.".format(v))
		if len(v)>1:
			errs.append("Multiple variables {0} assigned to the same helper.".format(str(v)))

	for v,c in constraints.items():
		for kw in c.keywords:
			if kw not in ChainMap(parent.namespace,helpers,constraints):
				errs.append("Variable '{0}' not found.".format(kw))
	cycle = check_cycle({v:c.keywords for v,c in constraints.items()})
	if len(cycle)>0:
		errs.append('Cyclical dependency found: {0}.'.format(cycle))

	namespace = dict()
	if len(errs)==0:
		namespace = merge_dicts([parent.namespace,helpers,{v:c.code for v,c in constraints.items()}])

	return namespace,errs


class Pattern(PatternArchetype):
	pass

class SpeciesPattern(PatternArchetype):
	pass

class FactoryPattern(PatternArchetype):
	def __init__(self,parent):
		self.prototype ,_ = GraphContainer.build(parent.get_connected())

	def create(self,varmap={}):
		return self.prototype.duplicate(varmap=varmap)._dict