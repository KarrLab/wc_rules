from template_molecular_graphs import *
from template_rules import *
from wc_rules.pattern import Pattern
from wc_rules.model import AggregateModel


pConstitutiveLynOnBeta = Pattern(gLynOnBeta,constraints = ['beta_left.ph == False','beta_right.ph==False'])
pConstitutiveLynOnGamma = Pattern(gLynOnGamma,constraints = ['beta_left.ph == False','gamma_right.ph==False'])
pConstitutiveLynOnSykLinker = Pattern(gLynOnSykLinker,constraints = ['beta_left.ph == False','linker_right.ph==False'])

constitutive_lyn_kinase = AggregateModel(
	name = 'constitutive',
	models = [
		TransPhosphorylationModel('lyn_on_beta', pConstitutiveLynOnBeta, 'beta_right'),
		TransPhosphorylationModel('lyn_on_gamma', pConstitutiveLynOnGamma, 'gamma_right'),
		TransPhosphorylationModel('lyn_on_syk_linker', pConstitutiveLynOnSykLinker, 'linker_right'),
	]
)

pActiveLynOnBeta = Pattern(gLynOnBeta,constraints = ['beta_left.ph == True','beta_right.ph==False'])
pActiveLynOnGamma = Pattern(gLynOnGamma,constraints = ['beta_left.ph == True','gamma_right.ph==False'])
pActiveLynOnSykLinker = Pattern(gLynOnSykLinker,constraints = ['beta_left.ph == True','linker_right.ph==False'])

active_lyn_kinase = AggregateModel(
	name = 'active',
	models = [
		TransPhosphorylationModel('lyn_on_beta', pActiveLynOnBeta, 'beta_right'),
		TransPhosphorylationModel('lyn_on_gamma', pActiveLynOnGamma, 'gamma_right'),
		TransPhosphorylationModel('lyn_on_syk_linker', pActiveLynOnSykLinker, 'linker_right'),
	]
)

model = AggregateModel(
	name = 'lyn_kinase',
	models = [
		constitutive_lyn_kinase,
		active_lyn_kinase
	]
)

data = {
	'constitutive': {
		'lyn_on_beta': {'phosphorylation_rate': 30},
		'lyn_on_gamma': {'phosphorylation_rate': 1},
		'lyn_on_syk_linker': {'phosphorylation_rate': 30}
	},
	'active': {
		'lyn_on_beta': {'phosphorylation_rate': 100},
		'lyn_on_gamma': {'phosphorylation_rate': 3},
		'lyn_on_syk_linker': {'phosphorylation_rate': 100}
	}
}
model.verify(data)
model.defaults = data