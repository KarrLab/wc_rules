
from ..utils.validate import *
from ..graph.collections import GraphContainer, GraphFactory
from .pattern import Pattern
from ..expressions.executable import ActionCaller,Constraint, Computation, RateLaw, initialize_from_string, ActionManager
from collections import Counter,ChainMap
from ..utils.collections import sort_by_value

class Rule:

	def __init__(self, name='', reactants=dict(), helpers=dict(), actions=[], factories=dict(),rate_prefix='', parameters = []):
		validate_keywords([name],'Rule name')
		self.name = name
		
		self.validate_reactants(reactants)
		self.reactants = reactants

		self.validate_helpers(helpers)
		self.helpers = helpers

		self.validate_factories(factories)
		self.factories = factories

		self.validate_parameters(parameters)
		self.parameters = parameters

		self.validate_namespace()

		newvars = self.validate_actions(actions)
		self.actions = actions

		self.validate_rate_prefix(rate_prefix)
		self.rate_prefix = rate_prefix

	@property
	def variables(self):
		return list(ChainMap(self.reactants,self.helpers,self.factories).keys()) + self.parameters 
	
	@property
	def namespace(self):
		d = dict()
		for r,x in self.reactants.items():
			d[r] = x.namespace
		for h in self.helpers:
			d[h] = "Helper Pattern"
		for p in self.parameters:
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
		
	def validate_factories(self,factories):
		validate_class(factories,dict,'Factories')
		validate_keywords(factories.keys(),'Factory')
		validate_dict(factories,GraphFactory,'Factory')

	def validate_parameters(self,params):
		validate_class(params,list,'Parameters')
		validate_keywords(params,'Parameter')
		
	def validate_namespace(self):
		names = [k for x in [self.reactants,self.helpers,self.factories] for k in x.keys()] + self.parameters
		assert len(names) == len(set(names)), 'Overlapping assignments found in rule namespace. Check reactants, helpers, factors.'


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
		namespace = list(self.reactants.keys()) + list(self.helpers.keys()) + self.parameters
		x = initialize_from_string(rate_prefix,(RateLaw,))
		validate_contains(self.variables,x.keywords,'Variable')

	def get_rate_law(self):
		return self.rate_prefix

	def get_rate_law_executable(self):
		return initialize_from_string(self.get_rate_law(),(RateLaw,))

	def get_action_executables(self):
		classes = (Constraint,Computation,ActionCaller)
		return [initialize_from_string(s,classes) for s in self.actions]

	def get_action_manager(self):
		return ActionManager(self.get_action_executables())	

class InstanceRateRule(Rule):

	def get_rate_law(self):
		reactant_sets = sort_by_value(self.reactants)
		elems = [f'comb({x[0]}.count(),{len(x)})' for x in reactant_sets]
		rate_law = "*".join([self.rate_prefix] + elems)
		return rate_law

