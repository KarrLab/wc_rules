from .pattern2 import PatternArchetype, check_cycle
from .utils import split_string, invert_dict
from .actions import ActionCaller
from .constraint import ExecutableExpression, Constraint, Computation, global_builtins
from collections import Counter
from pprint import pformat

class RateLaw(ExecutableExpression):
	start = 'expression'
	builtins = global_builtins
	allowed_forms = ['<expr>']
	allowed_returns = (int,float,)

class RuleArchetype:
	
	def __init__(self,reactants,helpers,actions,rate_law,params,namespace):
		self.reactants = reactants
		self.helpers = helpers
		self.actions = actions
		self.rate_law = rate_law
		self.params = params
		self.namespace = namespace

	def pprint_namespace(self):
		# in Python 3.8, sort_dicts=False to preserve insertion order
		return pformat(self.namespace)
		
	@classmethod
	def build(cls,reactants={},helpers={},actions='',rate_law=0,params=tuple()):
		# collect and verify reactants
		# collect and verify helpers
		# parse and compile actions
		# parse and compile rate law
		# verify and compile namespace
		for x in reactants.values():
			assert isinstance(x,PatternArchetype), x + " is not a pattern."
		for x in helpers.values():
			assert isinstance(x,PatternArchetype), x + " is not a pattern."
		actions = ExecutableExpression.initialize_from_strings(split_string(actions),[Constraint,Computation,ActionCaller])
		rate_law = RateLaw.initialize(str(rate_law))
		assert rate_law is not None, 'Could not create a valid rate law object.'
		for x in params:
			assert isinstance(x,str), x + " is not a parameter"
		namespace,errs = verify_and_compile_namespace(reactants,helpers,actions,rate_law,params)
		assert len(errs)==0, "Errors in namespace:\n{0}".format('\n'.join(errs))
		
		# TODO:
		# GET CANONICAL FROM 
		# GET CANONICAL ORDERING
		# STORE IT

		return cls(reactants=reactants,helpers=helpers,actions=actions,rate_law=rate_law,params=params,namespace=namespace)

	def fire(self,pool,idxmap):
		for action in self.actions:
			action.execute(pool,idxmap)
		return self

def verify_and_compile_namespace(reactants,helpers,actions,rate_law,params):
	errs = []

	varcount = Counter()
	for d in [reactants,helpers,actions]:
		varcount.update(d.keys())
	for var in varcount:
		if varcount[var]>1:
			errs.append("Variable {0} assigned multiple times.".format(var))
	inv_helpers = invert_dict(helpers)
	for h,v in inv_helpers.items():
		if not isinstance(h,PatternArchetype):
			errs.append("Helper variable '{0}' must be assigned to a PatternArchetype instance.".format(v))
		if len(v)>1:
			errs.append("Multiple variables {0} assigned to the same helper.".format(str(v)))

	allowed_keywords = [*reactants.keys(),*helpers.keys(),*actions.keys(),*params]
	for c in [*actions.values(),rate_law]:
		for kw in c.keywords:
			if kw not in allowed_keywords:
				errs.append("Variable/parameter {0} not found.".format(kw))

	cycle = check_cycle({v:c.keywords for v,c in actions.items()})
	if len(cycle)>0:
		errs.append('Cyclical dependency found: {0}.'.format(cycle))

	namespace=dict()
	if len(errs)==0:
		namespace = dict(
			reactants = {r:p.namespace for r,p in reactants.items()},
			helpers = {h:p.namespace for h,p in helpers.items()},
			actions = {a:c.code for a,c in actions.items()},
			rate_law = rate_law.code,
			params = tuple(params)
		)
	return namespace,errs

class TotalRateRule(RuleArchetype):
	# default behavior total rate
	pass


class InstanceRateRule(RuleArchetype):

	@classmethod
	def build(cls,reactants={},helpers={},actions='',rate_law=0,params=[]):
		rate_law = "({0})*({1})".format(str(rate_law),cls.rate_law_counts(reactants))
		return super().build(reactants,helpers,actions,rate_law,params)

	@classmethod
	def rate_law_counts(cls,reactants):
		reactant_counts = Counter(reactants.values())
		reactant_labels = {x:y[0] for x,y in invert_dict(reactants).items()}
		reaction_stoich = {reactant_labels[r]:reactant_counts[r] for r in reactant_counts}
		terms = ['comb({p}.count(),{n})'.format(p=p,n=n) for p,n in reaction_stoich.items()]
		rate_law_string = '*'.join(terms)
		return rate_law_string
