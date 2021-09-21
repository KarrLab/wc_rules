from wc_rules.modeling.pattern import Pattern
from wc_rules.modeling.rule import Rule
from wc_rules.modeling.model import RuleBasedModel

class BindingModel(RuleBasedModel):
	defaults = {'association_constant':1.0, 'dissociation_constant':1.0}

	def __init__(self,name,reactants,targets):
		(a,p), (b,q), (c,r) = reactants.items()
		s,t = targets
		binding_rule = Rule(
			name = 'binding_rule',
			reactants = {
				a: Pattern(p, constraints = [f'len({s}.bond)==0']),
				b: Pattern(q, constraints = [f'len({t}.bond)==0'])
				},
			actions = [f'{a}.{s}.add_bond({b}.{t})'],
			rate_prefix = 'association_constant',
			parameters = ['association_constant'],
			)
		unbinding_rule = Rule(
			name = 'unbinding_rule',
			reactants = {c: Pattern(r)},
			actions = [f'{c}.{s}.remove_bond()'],
			rate_prefix = 'dissociation_constant',
			parameters = ['dissociation_constant'],
			)
		super().__init__(name,rules=[binding_rule,unbinding_rule])
		self.verify(self.defaults)


class TransPhosphorylationModel(RuleBasedModel):

	defaults = {'phosphorylation_rate':1.0}

	def __init__(self,name,target,substrate):
		constraints = [f'len({target}.bond) == 0',f'{target}.ph == False']
		phosphorylation_rule = Rule(
			name = 'phosphorylation_rule',
			reactants = {'rSubstrate':Pattern(substrate,constraints=constraints)},
			actions = [f'rSubstrate.{target}.setTrue_ph()'],
			rate_prefix = 'phosphorylation_rate',
			parameters = ['phosphorylation_rate']
			)

		super().__init__(name,rules= [phosphorylation_rule])
		self.verify(self.defaults)


class DephosphorylationModel(RuleBasedModel):
	
	defaults = {'dephosphorylation_rate':1.0}

	def __init__(self,name,substrate):
		constraints = ['len(phosphosite.bond) == 0', 'phosphosite.ph == True']
		dephosphorylation_rule = Rule(
			name = f'dephosphorylation_rule',
			reactants = {'rSubstrate':Pattern(substrate,constraints=constraints)},
			actions = [f'rSubstrate.phosphosite.setFalse_ph()'],
			rate_prefix = 'dephosphorylation_rate',
			parameters = ['dephosphorylation_rate']
		)
		super().__init__(name,rules =[dephosphorylation_rule])
		self.verify(self.defaults)

