
from ..utils.validate import *
from ..graph.collections import GraphContainer
from ..utils.collections import split_string
from ..expressions.executable import Constraint, Computation, initialize_from_string, ExecutableExpressionManager
from attrdict import AttrDict


def make_attr_constraints(attrs):
	return [f'{var}.{attr} == {value}' for var,d in attrs.items() for attr,value in d.items()]

class Pattern:

	def __init__(self, parent=GraphContainer(), helpers=dict(), constraints = [], parameters= []):
		parent, attrs = self.validate_parent(parent)
		self.parent = parent

		self.validate_helpers(helpers)
		self.helpers = helpers

		self.validate_parameters(parameters)
		self.parameters = parameters
		
		self.assigned_variables = self.validate_constraints(constraints)
		self.constraints = make_attr_constraints(attrs) + constraints

	@property
	def variables(self):
		return list(self.namespace.keys())
	
	@property
	def namespace(self):
		d = dict()
		d.update(self.parent.namespace)
		for h in self.helpers:
			d[h] = "Helper Pattern"
		for p in self.parameters:
			d[p] = "Parameter"
		for v  in self.assigned_variables:
			d[v] = "Assigned Variable"
		return d

	@property
	def cache_variables(self):
		if isinstance(self.parent,GraphContainer):
			return self.parent.variables + self.assigned_variables
		return self.parent.cache_variables + self.assigned_variables

	def asdict(self):
		return dict(**self.namespace,constraints=self.constraints)

	def validate_parent(self,parent):
		validate_class(parent,(GraphContainer,Pattern),'Parent')
		if isinstance(parent,GraphContainer):
			parent.validate_connected()
			validate_keywords(parent._dict.keys(),'Parent Variable')
			for idx,node in parent.iter_nodes():
				validate_literal_attributes(node)
				validate_related_attributes(node)
			parent,attrs = parent.strip_attrs()
			return parent,attrs
		return parent,{}

	def validate_helpers(self,helpers):
		validate_class(helpers,dict,'Helpers')
		validate_keywords(helpers.keys(),'Helper')
		validate_unique(self.parent.variables,helpers.keys(),'Helper')
		validate_dict(helpers,Pattern,'Helper')
		
	def validate_parameters(self,parameters):
		validate_class(parameters,list,'Parameters')
		validate_keywords(parameters,'Parameter')
		validate_unique(self.parent.variables + list(self.helpers.keys()), parameters, 'Parameter')
		
	def validate_constraints(self,constraints):
		validate_class(constraints,list,'Constraints')
		validate_list(constraints,str,'Constraint')

		namespace = self.parent.variables + list(self.helpers.keys()) + self.parameters
		newvars, kwdeps, executables = [] , {}, []

		for s in constraints:
			x = initialize_from_string(s,(Constraint,Computation))
			validate_contains(namespace + newvars,x.keywords,'Variable')
			if isinstance(x,Computation):
				v = x.deps.declared_variable
				validate_keywords([v],'Variable')
				validate_unique(namespace + newvars,[v],'Variable')
				newvars.append(v)
				kwdeps[v] = x.keywords
			executables.append(x)
		validate_acyclic(kwdeps)

		return newvars

	def make_executable_constraints(self):
		# mark for downgrade
		return [initialize_from_string(s,(Constraint,Computation)) for s in self.constraints]

	def make_executable_constraint(self,s):
		return initialize_from_string(s,(Constraint,Computation))

	def make_executable_expression_manager(self):
		execs = [initialize_from_string(s,(Constraint,Computation)) for s in self.constraints]
		manager = ExecutableExpressionManager(execs,self.namespace)
		return manager

	def get_initialization_code(self):
		code = AttrDict({
			'parent': None,
			'constraints': bool(self.constraints),
			'helpers': bool(self.helpers)
			})
		if isinstance(self.parent,GraphContainer) and len(self.parent)>0:
			code['parent'] = 'graph'
		elif isinstance(self.parent,Pattern):
			code['parent'] = 'pattern'

		if not any([code.helpers,code.constraints]):
			code['subtype'] = 'alias'		
		elif not code.helpers:
			code['subtype'] = 'no_helpers'
		return code