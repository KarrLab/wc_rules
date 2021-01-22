from .pattern2 import PatternArchetype
from .utils import split_string
from .actions import ActionCaller
from .constraint import ExecutableExpression, Constraint, Computation
from collections import Counter

class RuleArchetype:
	
	def __init__(self,reactants={},helpers={},actions={},rate_constant='1'):
		self.reactants = reactants
		self.helpers = helpers
		self.actions = actions
		self.rate_constant = rate_constant

	@classmethod
	def build(cls,reactants={},helpers={},actions='',rate_constant=1,reaction_paths=None):
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
		if reaction_paths is None:
			reactant_counts = Counter(reactants.values())
			encountered = dict()
			for r,x in reactants.items():
				if x not in encountered.values():
					encountered[r] = x
			reaction_stoichiometry = {x:reactant_counts[y] for x,y in encountered.items()}
			terms = ['comb({p}.count(),{n})'.format(p=p,n=n) for p,n in reaction_stoichiometry.items()]
			rate_law_string = '*'.join(['({0})'.format(rate_constant)] + terms)
			print(reaction_stoichiometry)
			print(rate_law_string)

		return cls(reactants=reactants,helpers=helpers,actions=actions)


	def fire(self,pool,idxmap):
		for action in self.actions:
			action.execute(pool,idxmap)
		return self

class Rule(RuleArchetype):
	pass

	