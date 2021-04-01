from wc_rules.rule import Rule
from wc_rules.model import RuleBasedModel


class BindingModel(RuleBasedModel):
	
	defaults = {'association_constant':1.0, 'dissociation_constant': 1.0}

	def __init__(self,name,inputs):
		# ni, pi, ti = name, pattern, target of bond
		tuple1, tuple2, tuple3 = inputs
		(n1,p1,t1), (n2,p2,t2), (n3,p3,t3) = tuple1, tuple2, tuple3
		
		binding_rule = Rule(
			name = f'{name}_binding_rule',
			reactants = {n1:p1,n2:p2},
			actions = [f'{n1}.{t1}.add_bond({n2}.{t2})'],
			rate_prefix = 'association_constant',
			params = ['association_constant']
			)

		unbinding_rule = Rule(
			name = f'{name}_unbinding_rule',
			reactants = {n3:p3},
			actions = [f'{n3}.{t3}.remove_bond()'],
			rate_prefix = 'dissociation_constant',
			params = ['dissociation_constant']
			)

		super().__init__(name,rules=[binding_rule,unbinding_rule])
		self.verify(self.defaults)

class TransPhosphorylationModel(RuleBasedModel):

	defaults = {'phosphorylation_rate':1.0}

	def __init__(self,name,pattern,target):

		phosphorylation_rule = Rule(
			name = f'{name}_phosphorylation_rule',
			reactants = {'reactant':pattern},
			actions = [f'reactant.{target}.setTrue_ph()'],
			rate_prefix = 'phosphorylation_rate',
			params = ['phosphorylation_rate']
			)

		super().__init__(name,rules= [phosphorylation_rule])
		self.verify(self.defaults)


class DephosphorylationModel(RuleBasedModel):
	
	defaults = {'dephosphorylation_rate':1.0}

	def __init__(self,name,pattern,target):

		dephosphorylation_rule = Rule(
			name = f'{name}_dephosphorylation_rule',
			reactants = {'reactant':pattern},
			actions = [f'reactant.{target}.setFalse_ph()'],
			rate_prefix = 'dephosphorylation_rate',
			params = ['dephosphorylation_rate']
		)
		super().__init__(name,rules =[dephosphorylation_rule])
		self.verify(self.defaults)


