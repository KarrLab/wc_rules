
from wc_rules.pattern import Pattern
from wc_rules.model import AggregateModel
from template_molecular_graphs import *
from template_rules import BindingModel

# Patterns
free_lyn = Pattern(gLyn,constraints = ['len(sh2.bond)==0'])
free_beta_u = Pattern(gReceptorBeta,constraints = ['beta.ph==False','len(beta.bond)==0'])
free_beta_p = Pattern(gReceptorBeta,constraints = ['beta.ph==True','len(beta.bond)==0'])

bound_lyn_u = Pattern(gLynReceptor,constraints = ['beta.ph==False'])
bound_lyn_p = Pattern(gLynReceptor,constraints = ['beta.ph==True'])

# binding models
constitutive_inputs = [
	('free_lyn',free_lyn,'sh2'),
	('free_beta',free_beta_u, 'beta'),
	('bound_lyn',bound_lyn_u,'sh2')
]
constitutive_model = BindingModel('constitutive', constitutive_inputs)

active_inputs = [
	('free_lyn',free_lyn,'sh2'),
	('free_beta',free_beta_p, 'beta'),
	('bound_lyn',bound_lyn_p,'sh2')
]
active_model = BindingModel('active', active_inputs)

model = AggregateModel(
	name = 'lyn_rec',
	models = [constitutive_model,active_model]
	)

data = {
	'constitutive': {'association_constant':5e-2, 'dissociation_constant':20.0},
	'active': {'association_constant':5e-2, 'dissociation_constant':0.12}
}
model.verify(data)
model.defaults = data
