from .indexer import GraphContainer
from .utils import generate_id,ValidateError,listmap, split_string, merge_dicts, no_overlaps, invert_dict
from .canonical import canonical_label
from .canonical_expr import canonical_expression_ordering
from functools import partial
from .constraint import global_builtins, Constraint
from functools import wraps
from .entity import Entity
from pprint import pformat
from collections import ChainMap, Counter, deque
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

	def get_canonical_form_partition(self):
		return self.variable_map.replace(self.canonical_form.partition)

	def get_canonical_form_leaders(self):
		return self.variable_map.replace(self.canonical_form.leaders)

class Pattern:

	def __init__(self,parent,helpers=dict(),constraints=dict(),namespace=dict(),partition=tuple(),leaders=tuple()):
		self.parent = parent
		self.helpers = helpers
		self.constraints = constraints
		self.namespace = namespace
		self.partition = partition
		self.leaders = leaders

	def get_canonical_form_partition(self):
		return self.parent.get_canonical_form_partition()

	def get_canonical_form_leaders(self):
		return self.parent.get_canonical_form_leaders()

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

		constraint_strings.extend(split_string(constraints))
		constraints = Constraint.initialize_strings(constraint_strings,cmax)

		namespace,errs = verify_and_compile_namespace(parent,helpers,constraints)
		assert len(errs)==0, "Errors in namespace:\n{0}".format('\n'.join(errs))

		seed = parent.get_canonical_form_partition()
		partition, leaders = canonical_expression_ordering(seed,namespace,constraints)
		return Pattern(parent,helpers,constraints,namespace,partition,leaders)

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

def check_cycle(gdict):
	# gdict is a directed graph represented as a dict
	nodes,paths = deque(gdict), deque()
	while nodes or paths:
		if not paths:
			paths.append([nodes.popleft()])
		path = paths.popleft()
		if len(path)>1 and path[0]==path[-1]:
			pathstr = '->'.join(path)
			return pathstr 
		next_steps = gdict.get(path[-1],[])
		if len(next_steps)>0:
			paths.extend([path + [x] for x in next_steps])
	return ''

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
		if not isinstance(h,Pattern):
			errs.append("Helper variable '{0}' must be assigned to a Pattern instance.".format(v))
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
		







