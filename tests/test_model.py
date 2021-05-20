from wc_rules.schema.chem import Molecule, Site
from wc_rules.schema.attributes import BooleanAttribute

from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.rule import Rule, InstanceRateRule
from wc_rules.modeling.model import RuleBasedModel, AggregateModel
from wc_rules.utils.validate import validate_list

import unittest

class Enzyme(Molecule):
	pass

class EnzymeActiveSite(Site):
	pass


class Substrate(Molecule):
	pass

class ModificationSite(Site):
	ph = BooleanAttribute()


class EnzymeSubstrateModel(RuleBasedModel):
	def process_inputs(self,enzyme,substrate):
		assert isinstance(enzyme,GraphContainer)
		assert isinstance(substrate,GraphContainer)
		return enzyme, substrate



class ExplicitMichaelisMentenModel(EnzymeSubstrateModel):

	defaults = dict(kf=1.0,kr=1.0,kcat=1.0)

	def __init__(self,name,enzyme,substrate):

		enzyme, substrate = self.process_inputs(enzyme,substrate)

		E = Pattern(enzyme, constraints = ['len(enzyme_site.bond) == 0'])

		S = Pattern(substrate, constraints = ['len(substrate_site.bond) == 0','substrate_site.ph == False'])
		
		g1, g2 = enzyme.duplicate(), substrate.duplicate()
		g1['enzyme_site'].bond = g2['substrate_site']
		es_complex = GraphContainer(g1['enzyme'].get_connected())
		
		ES = Pattern(es_complex, constraints = ['substrate_site.ph == False'])

		binding_rule = InstanceRateRule(
			name = 'binding_rule',
			reactants = dict(enzyme=E,substrate=S),
			actions = ['enzyme.enzyme_site.add_bond(substrate.substrate_site)'],
			rate_prefix = 'kf',
			parameters = ['kf']
		)

		unbinding_rule = InstanceRateRule(
			name = 'unbinding_rule',
			reactants = dict(enzyme_substrate_complex = ES),
			actions = ['enzyme_substrate_complex.substrate_site.remove_bond()'],
			rate_prefix = 'kr',
			parameters = ['kr']
			)

		catalytic_rule = InstanceRateRule(
			name = 'catalytic_rule',
			reactants = dict(enzyme_substrate_complex = ES),
			actions = [
				f'enzyme_substrate_complex.substrate_site.setTrue_ph()',
				f'enzyme_substrate_complex.substrate_site.remove_bond()'
				],
			rate_prefix = 'kcat',
			parameters = ['kcat']
			)


		super().__init__(name,rules=[binding_rule,unbinding_rule,catalytic_rule])
		self.verify(self.defaults)

class ImplicitMichaelisMentenModel(EnzymeSubstrateModel):

	defaults = dict(kcat=1.0,KM=1.0)

	def __init__(self,name,enzyme,substrate):
		enzyme, substrate, = self.process_inputs(enzyme,substrate)

		E = Pattern(enzyme)
		S = Pattern(substrate, constraints = ['len(substrate_site.bond) == 0','substrate_site.ph == False'])
		
		catalytic_rule = Rule(
			name = 'catalytic_rule',
			reactants = dict(substrate=S),
			helpers = dict(enzyme=E),
			actions = ['substrate.substrate_site.setTrue_ph()'],
			rate_prefix = 'kcat*enzyme.count()*substrate.count()/(KM + substrate.count())',
			parameters = ['kcat','KM']
			)

		super().__init__(name,rules=[catalytic_rule])
		self.verify(self.defaults)


def make_enzyme():
	x = Enzyme('enzyme',sites=[EnzymeActiveSite('enzyme_site')])
	return GraphContainer(x.get_connected())

def make_substrate():
	x = Substrate('substrate',sites=[ModificationSite('substrate_site')])
	return GraphContainer(x.get_connected())

class TestRuleBasedModel(unittest.TestCase):


	def test_explicit_MM(self):
		model = ExplicitMichaelisMentenModel('explicit_MM',make_enzyme(),make_substrate())

		data = dict(kf=2.0,kr=2.0,kcat=2.0)
		model.verify(data)

	def test_implicit_MM(self):
		model = ImplicitMichaelisMentenModel('implicit_MM',make_enzyme(),make_substrate())

		data = dict(kcat=2.0,KM=2.0)
		model.verify(data)
