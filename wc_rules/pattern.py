from dataclasses import dataclass
from .validate_helpers import *
from .indexer import GraphContainer
from .utils import split_string, check_cycle
from .constraint import Constraint, Computation, initialize_from_strings

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
		for h,p in self.helpers.items():
			d[h] = "Helper {0}".format(p)
		for p in self.params:
			d[p] = "Parameter"
		for v  in self.assigned_variables:
			d[v] = "Assigned Variable"
		return d

	def validate_parent(self,parent):
		validate_class(parent,(GraphContainer,Pattern),'Parent')
		if isinstance(parent,GraphContainer):
			parent.validate_connected()
			for idx,node in parent.iternodes():
				validate_keyword(idx,'Variable')
				validate_literal_attributes(node)
				validate_related_attributes(node)

	def validate_helpers(self,helpers):
		validate_class(helpers,dict,'Helpers')
		for h,x in helpers.items():
			validate_keyword(h,'Helper')
			validate_unique(self.parent.variables,[h],'Helper')
			validate_class(x,Pattern,'Helper')

	def validate_params(self,params):
		validate_class(params,list,'Parameters')
		for elem in params:
			validate_keyword(elem,'Parameter')

	def validate_constraints(self,constraints):
		validate_class(constraints,list,'Constraints')
		namespace = self.parent.variables + list(self.helpers.keys()) + self.params
		newvars = []
		for s in constraints:
			x = initialize_from_strings(s,(Constraint,Computation))
			print(s,x)
			validate_contains(namespace + newvars,x.keywords,'Variable')
			if isinstance(x,Computation):
				v = x.deps.declared_variable
				validate_keyword(v,'Variable')
				validate_unique(namespace + newvars,v,'Variable')
				newvars.append(v)
		return newvars