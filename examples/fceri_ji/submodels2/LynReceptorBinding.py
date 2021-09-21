from .graphs import build_Lyn, build_receptor, recruit_to_receptor
from .templates import BindingModel

from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.model import AggregateModel

gSH2 = build_Lyn()
gBeta = build_receptor(['beta'])
gSH2BetaBond = recruit_to_receptor(build_receptor(['beta']),build_Lyn())

class LynReceptorBindingModel(BindingModel):

	def __init__(self,name,phosphorylation_state):
		constraints = [f'beta.ph == {phosphorylation_state}']
		reactants = {
			'SH2': gSH2,
			'Beta': Pattern(gBeta, constraints = constraints),
			'SH2BetaBond': Pattern(gSH2BetaBond, constraints = constraints)
		}
		targets = ['sh2','beta']
		return super().__init__(name,reactants,targets)

model = AggregateModel(
	name = 'lyn_receptor',
	models = [ 
		LynReceptorBindingModel('constitutive',phosphorylation_state=False),
		LynReceptorBindingModel('active',phosphorylation_state=True)
		]
	)

data = {
	'constitutive': {
		'association_constant':		5e-2, 
		'dissociation_constant':	20.0
	},
	'active': {
		'association_constant':		5e-2, 
		'dissociation_constant':	0.12
	}
}
model.verify(data)
model.defaults = data
