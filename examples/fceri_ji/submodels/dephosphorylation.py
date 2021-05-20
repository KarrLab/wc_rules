from ..templates.graphs import *
from ..templates.rules import DephosphorylationModel
from wc_rules.modeling.pattern import Pattern
from wc_rules.modeling.model import AggregateModel

def build_model(name,reactant):
	return DephosphorylationModel(
		name = name,
		reactant = reactant,
		target = 'phosphosite'
		)

dephos_configurations = {
	'receptor': 	Pattern(gRecPhospho,constraints = ['len(phosphosite.bond)==0', 'phosphosite.ph==True']),
	'membrane_syk': Pattern(gSykPhospho,constraints = ['len(tsh2.bond)==1', 'phosphosite.ph==True']),
	'free_syk': 	Pattern(gSykPhospho,constraints = ['len(tsh2.bond)==0', 'phosphosite.ph==True'])
}


model = AggregateModel(
	name = 'dephosphorylation',
	models = [ build_model(name,reactant) for name, reactant in dephos_configurations.items()]
)

data = {
	'receptor': 	{'dephosphorylation_rate': 20.0},
	'membrane_syk': {'dephosphorylation_rate': 20.0},
	'free_syk':		{'dephosphorylation_rate': 20.0}
}

model.verify(data)
model.defaults = data
