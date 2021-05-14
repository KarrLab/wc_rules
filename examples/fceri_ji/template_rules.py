
from wc_rules.modeling.rule import Rule
from wc_rules.modeling.model import RuleBasedModel

class BindingModel(RuleBasedModel):
	
	defaults = {'association_constant':1.0, 'dissociation_constant': 1.0}

	def __init__(self,name,reactants,targets):
		# assume reactants are provided in order
		n1, n2, n3 = reactants.keys()
		
		binding_rule = Rule(
			name = f'{name}_binding_rule',
			reactants = {n1:reactants[n1],n2:reactants[n2]},
			actions = [f'{n1}.{targets[n1]}.add_bond({n2}.{targets[n2]})'],
			rate_prefix = 'association_constant',
			params = ['association_constant']
			)

		unbinding_rule = Rule(
			name = f'{name}_unbinding_rule',
			reactants = {n3:reactants[n3]},
			actions = [f'{n3}.{targets[n3]}.remove_bond()'],
			rate_prefix = 'dissociation_constant',
			params = ['dissociation_constant']
			)

		super().__init__(name,rules=[binding_rule,unbinding_rule])
		self.verify(self.defaults)

class TransPhosphorylationModel(RuleBasedModel):

	defaults = {'phosphorylation_rate':1.0}

	def __init__(self,name,reactant,target):

		phosphorylation_rule = Rule(
			name = f'{name}_phosphorylation_rule',
			reactants = {'reactant':reactant},
			actions = [f'reactant.{target}.setTrue_ph()'],
			rate_prefix = 'phosphorylation_rate',
			params = ['phosphorylation_rate']
			)

		super().__init__(name,rules= [phosphorylation_rule])
		self.verify(self.defaults)


class DephosphorylationModel(RuleBasedModel):
	
	defaults = {'dephosphorylation_rate':1.0}

	def __init__(self,name,reactant,target):

		dephosphorylation_rule = Rule(
			name = f'{name}_dephosphorylation_rule',
			reactants = {'reactant':reactant},
			actions = [f'reactant.{target}.setFalse_ph()'],
			rate_prefix = 'dephosphorylation_rate',
			params = ['dephosphorylation_rate']
		)
		super().__init__(name,rules =[dephosphorylation_rule])
		self.verify(self.defaults)
