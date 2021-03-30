
from .validate_helpers import *
from .indexer import GraphContainer
from .utils import split_string, check_cycle, idgen
from .executable_expr import Constraint, Computation, initialize_from_string
    	
class Pattern:

	def __init__(self, parent=GraphContainer(), helpers=dict(), constraints = [], params= []):
		self.validate_parent(parent)
		self.parent = parent

		self.validate_helpers(helpers)
		self.helpers = helpers

		self.validate_params(params)
		self.params = params
		
		self.assigned_variables = self.validate_constraints(constraints)
		self.constraints = constraints

	@property
	def variables(self):
		return self.parent.variables + list(self.helpers.keys()) + self.params + self.assigned_variables
	
	@property
	def namespace(self):
		d = dict()
		d.update(self.parent.namespace)
		for h in self.helpers:
			d[h] = "Helper Pattern"
		for p in self.params:
			d[p] = "Parameter"
		for v  in self.assigned_variables:
			d[v] = "Assigned Variable"
		return d

	def asdict(self):
		return dict(**self.namespace,constraints=self.constraints)

	def validate_parent(self,parent):
		validate_class(parent,(GraphContainer,Pattern),'Parent')
		if isinstance(parent,GraphContainer):
			parent.validate_connected()
			validate_keywords(parent._dict.keys(),'Parent Variable')
			for idx,node in parent.iternodes():
				validate_literal_attributes(node)
				validate_related_attributes(node)

	def validate_helpers(self,helpers):
		validate_class(helpers,dict,'Helpers')
		validate_keywords(helpers.keys(),'Helper')
		validate_unique(self.parent.variables,helpers.keys(),'Helper')
		validate_dict(helpers,Pattern,'Helper')
		
	def validate_params(self,params):
		validate_class(params,list,'Parameters')
		validate_keywords(params,'Parameter')
		validate_unique(self.parent.variables + list(self.helpers.keys()), params, 'Parameter')
		
	def validate_constraints(self,constraints):
		validate_class(constraints,list,'Constraints')
		validate_list(constraints,str,'Constraint')

		namespace = self.parent.variables + list(self.helpers.keys()) + self.params
		newvars, kwdeps = [] , {}
		for s in constraints:
			x = initialize_from_string(s,(Constraint,Computation))
			validate_contains(namespace + newvars,x.keywords,'Variable')
			if isinstance(x,Computation):
				v = x.deps.declared_variable
				validate_keywords([v],'Variable')
				validate_unique(namespace + newvars,[v],'Variable')
				newvars.append(v)
				kwdeps[v] = x.keywords
		validate_acyclic(kwdeps)
		return newvars

class SynthesisPattern:

	def __init__(self,prototype):
		err = "FactoryPattern must be initialized from a GraphContainer with a connected graph."
		assert isinstance(prototype,GraphContainer) and prototype.validate_connected(), err
		self.prototype = prototype

