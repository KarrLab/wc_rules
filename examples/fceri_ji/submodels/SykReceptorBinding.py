
from wc_rules.modeling.pattern import Pattern
from wc_rules.modeling.model import AggregateModel
from ..templates.graphs import *
from ..templates.rules import BindingModel

# Patterns
free_syk = Pattern(gSykTsh2,constraints = ['len(tsh2.bond)==0'])
free_gamma = Pattern(gReceptorGamma,constraints = ['gamma.ph==True','len(gamma.bond)==0'])
bound_syk = Pattern(gSykReceptor,constraints = ['gamma.ph==True'])

model = BindingModel(
	name = 'syk_receptor',
	reactants = {
		'rSyk': 		free_syk,
		'rReceptor': 	free_gamma,
		'rSykReceptor': bound_syk
		},
	targets = {
		'rSyk': 		'tsh2',
		'rReceptor': 	'gamma',
		'rSykReceptor': 'tsh2'
		}
)

data = {
	'association_constant':		6e-2, 
	'dissociation_constant':	20.0
}

model.verify(data)
model.defaults = data