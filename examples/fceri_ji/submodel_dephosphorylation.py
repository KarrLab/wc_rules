from template_molecular_graphs import *
from template_rules import DephosphorylationModel
from wc_rules.pattern import Pattern
from wc_rules.model import AggregateModel


receptor_dephos_model = DephosphorylationModel(
	name = 'receptor',
	pattern = Pattern(gRecPhospho,constraints = ['len(phosphosite.bond)==0', 'phosphosite.ph==True']),
	target = 'phosphosite'
)


membrane_syk_dephos_model = DephosphorylationModel(
	name = 'membrane_syk',
	pattern = Pattern(gSykPhospho,constraints = ['len(tsh2.bond)==1', 'phosphosite.ph==True']),
	target = 'phosphosite'
)

free_syk_dephos_model = DephosphorylationModel(
	name = 'free_syk',
	pattern = Pattern(gSykPhospho,constraints = ['len(tsh2.bond)==0', 'phosphosite.ph==True']),
	target = 'phosphosite'
)

syk_dephos_model = AggregateModel(
	name = 'syk',
	models = [membrane_syk_dephos_model, free_syk_dephos_model]
)

model = AggregateModel(
	name = 'dephosphorylation',
	models = [ receptor_dephos_model, syk_dephos_model ]
)

data = {
	'receptor': { 'dephosphorylation_rate': 20.0 },
	'syk':
		{
		'membrane_syk': { 'dephosphorylation_rate': 20.0},
		'free_syk': {'dephosphorylation_rate': 20.0}
		}
}

model.verify(data)
model.defaults = data
