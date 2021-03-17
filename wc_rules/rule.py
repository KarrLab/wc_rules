
from .validate_helpers import *
from .pattern import Pattern
from .actions import ActionCaller
from .executable_expr import Constraint, Computation, RateLaw, initialize_from_string

class Rule:

	def __init__(self, reactants=dict(), helpers=dict(), actions=[], rate_prefix='', params = []):
		self.validate_reactants(reactants)
		self.reactants = reactants

		self.validate_helpers(helpers)
		self.helpers = helpers

		self.validate_params(params)
		self.params = params

		newvars = self.validate_actions(actions)
		self.actions = actions

		self.validate_rate_prefix(rate_prefix)
		self.rate_prefix = rate_prefix

	@property
	def variables(self):
		return list(self.reactants.keys()) + list(self.helpers.keys()) + self.params 
	
	@property
	def namespace(self):
		d = dict()
		for r,x in self.reactants.items():
			d[r] = x.namespace
		for h in self.helpers:
			d[h] = "Helper Pattern"
		for p in self.params:
			d[p] = "Parameter"
		return d

	def asdict(self):
		return dict(**self.namespace,actions=self.actions,rate_prefix=self.rate_prefix)

	def validate_reactants(self,reactants):
		validate_class(reactants,dict,'Reactants')
		validate_keywords(reactants.keys(),'Reactant')
		validate_dict(reactants,Pattern,'Reactant')
		
	def validate_helpers(self,helpers):
		validate_class(helpers,dict,'Helpers')
		validate_keywords(helpers.keys(),'Helper')
		validate_dict(helpers,Pattern,'Helper')
		validate_unique(self.reactants.keys(),helpers.keys(), 'Helper')

	def validate_params(self,params):
		validate_class(params,list,'Parameters')
		validate_keywords(params,'Parameter')
		validate_unique(list(self.reactants.keys()) + list(self.helpers.keys()), params, 'Parameter')

	def validate_actions(self,actions):
		validate_class(actions,list,'Actions')
		validate_list(actions,str,'Action')

		newvars, kwdeps = [] , {}
		for s in actions:
			x = initialize_from_string(s,(Constraint,Computation,ActionCaller))
			validate_contains(self.variables + newvars,x.keywords,'Variable')
			if isinstance(x,Computation):
				v = x.deps.declared_variable
				validate_keywords([v],'Variable')
				validate_unique(self.variables + newvars,[v],'Variable')
				newvars.append(v)
				kwdeps[v] = x.keywords
		validate_acyclic(kwdeps)
		return newvars

	def validate_rate_prefix(self,rate_prefix):
		validate_class(rate_prefix,str,'Rate prefix')
		namespace = list(self.reactants.keys()) + list(self.helpers.keys()) + self.params
		x = initialize_from_string(rate_prefix,(RateLaw,))
		validate_contains(self.variables,x.keywords,'Variable')
