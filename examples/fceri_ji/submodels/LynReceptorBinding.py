
from wc_rules.modeling.pattern import Pattern
from wc_rules.modeling.model import AggregateModel
from ..templates.graphs import *
from ..templates.rules import BindingModel

# Patterns
free_lyn = Pattern(gLyn, constraints = ['len(sh2.bond)==0'])
free_beta_u = Pattern(gReceptorBeta, constraints = ['beta.ph==False','len(beta.bond)==0'])
free_beta_p = Pattern(gReceptorBeta, constraints = ['beta.ph==True','len(beta.bond)==0'])

bound_lyn_u = Pattern(gLynReceptor, constraints = ['beta.ph==False'])
bound_lyn_p = Pattern(gLynReceptor, constraints = ['beta.ph==True'])

constitutive_model = BindingModel(
	name = 'constitutive',
	reactants = {
		'rLyn':			free_lyn,
		'rReceptor':	free_beta_u,
		'rLynReceptor':	bound_lyn_u,
		},
	targets = {
		'rLyn':			'sh2',
		'rReceptor':	'beta',
		'rLynReceptor':	'sh2',
		}
	)

active_model = BindingModel(
	name = 'active',
	reactants = {
		'rLyn':			free_lyn,
		'rReceptor':	free_beta_p,
		'rLynReceptor':	bound_lyn_p,
		},
	targets = {
		'rLyn':			'sh2',
		'rReceptor':	'beta',
		'rLynReceptor':	'sh2',
		}
	)

model = AggregateModel(
	name = 'lyn_receptor',
	models = [ constitutive_model,active_model ]
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
