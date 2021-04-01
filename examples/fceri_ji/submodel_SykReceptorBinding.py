
from wc_rules.pattern import Pattern
from wc_rules.model import AggregateModel
from template_molecular_graphs import *
from template_rules import BindingModel

# Patterns
free_syk = Pattern(gSykTsh2,constraints = ['len(tsh2.bond)==0'])
free_gamma = Pattern(gReceptorGamma,constraints = ['gamma.ph==True','len(gamma.bond)==0'])
bound_syk = Pattern(gSykReceptor,constraints = ['gamma.ph==True'])


# binding model inputs
inputs = [
	('free_syk',free_syk,'tsh2'),
	('free_gamma',free_gamma, 'gamma'),
	('bound_syk',bound_syk,'tsh2')
]

model = BindingModel('syk_rec', inputs)

data = {'association_constant':6e-2, 'dissociation_constant':20.0}
model.verify(data)
model.defaults = data