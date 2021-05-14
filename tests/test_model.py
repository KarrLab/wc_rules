from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.rule import Rule
from wc_rules.modeling.model import RuleBasedModel, AggregateModel

import unittest

class EnzymeSubstrateModel(RuleBasedModel):

	defaults = {'kf':1.0, 'kr':1.0, 'KM':1.0}

	def __init__(self,name,enzyme,substrate,enzyme_site,substrate_site):
		assert isinstance(enzyme,GraphContainer)
		assert isinstance(substrate,GraphContainer)

		enzyme = Pattern(enzyme, constraints = [f'len(enzyme.{enzyme_site}.bond) == 0'])
		substrate = Pattern(substrate, constraints = [f'len(substrate.{substrate_site}.bond) == 0'])
		binding_rule = Rule(
			reactants = dict(enzyme=enzyme,substrate=substrate),
			actions = [f'enzyme.{enzyme_site}.add_bond(substrate.{substrate_site})'],
			rate_prefix = 'kf',
			parameters = ['kf']
		)

		super().__init__(name,rules=[binding_rule])
		self.verify(self.defaults)

class TestRuleBasedModel(unittest.TestCase):


	def test_explicit_MM(self):
		pass

	def test_implicit_MM(self):
		pass