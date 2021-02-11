from .pattern2 import PatternArchetype
from .utils import split_string, invert_dict
from .actions import ActionCaller
from .constraint import ExecutableExpression, Constraint, Computation, global_builtins
from collections import Counter

class RateLaw(ExecutableExpression):
	start = 'expression'
	builtins = global_builtins
	allowed_forms = ['<expr>']
	allowed_returns = (int,float,)

class RuleArchetype:
	
	def __init__(self,reactants={},helpers={},actions={},rate_constant='1',rate_law = RateLaw.initialize('1')):
		self.reactants = reactants
		self.helpers = helpers
		self.actions = actions
		self.rate_constant = rate_constant
		self.rate_law = rate_law

	@classmethod
	def build(cls,reactants={},helpers={},actions='',rate_constant='1',params={},counts=True):
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
		rate_law_string = str(rate_constant)
		if counts and len(reactants)>0:	
			rate_law_string = '({0})*{1}'.format(rate_constant,cls.rate_law_counts(reactants))
		else:
			rate_law_string = rate_constant
		rate_law = RateLaw.initialize(rate_law_string)
		assert rate_law is not None, 'Could not create a valid rate law object.'
		return cls(reactants=reactants,helpers=helpers,actions=actions,rate_constant=rate_constant,rate_law=rate_law)

	@classmethod
	def rate_law_counts(cls,reactants):
		reactant_counts = Counter(reactants.values())
		reactant_labels = {x:y[0] for x,y in invert_dict(reactants).items()}
		reaction_stoich = {reactant_labels[r]:reactant_counts[r] for r in reactant_counts}
		terms = ['comb({p}.count(),{n})'.format(p=p,n=n) for p,n in reaction_stoich.items()]
		rate_law_string = '*'.join(terms)
		return rate_law_string

	def fire(self,pool,idxmap):
		for action in self.actions:
			action.execute(pool,idxmap)
		return self

class Rule(RuleArchetype):
	pass

	