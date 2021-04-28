
from wc_rules.pattern import Pattern
from wc_rules.model import AggregateModel
from template_molecular_graphs import *
from template_rules import BindingModel

# Pattern template
def build_ligand_pattern(v1,v2):
	constraints = [f'len(fc1.bond) == {v1}',f'len(fc2.bond) == {v2}']
	return Pattern(gLigand,constraints=constraints)

# Patterns
L00 = build_ligand_pattern(0,0)
L01 = build_ligand_pattern(0,1)
L11 = build_ligand_pattern(1,1)
R   = Pattern(gReceptorAlpha,constraints = ['len(alpha.bond) == 0'])

monomer_model = BindingModel(
	name = 'monomer',
	reactants = {
		'rLigand': 			L00, 
		'rReceptor': 		R, 
		'rLigandReceptor':	L01
		},
	targets = {
		'rLigand': 			'fc2', 
		'rReceptor': 		'alpha', 
		'rLigandReceptor': 	'fc2'
		}
	)

dimer_model = BindingModel(
	name = 'dimer',
	reactants = {
		'rLigand': 			L01, 
		'rReceptor': 		R, 
		'rLigandReceptor':	L11
		},
	targets = {
		'rLigand': 			'fc1', 
		'rReceptor': 		'alpha', 
		'rLigandReceptor': 	'fc1'
		}
	)

# Aggregate model
model = AggregateModel(
	name = 'ligand_receptor',
	models = [ monomer_model, dimer_model ]
	)

# setting default parameters
data = {
	'monomer': {
		'association_constant':		1.3e-7, 
		'dissociation_constant':	0.0
	},
	'dimer': {
		'association_constant':		2.5e-1, 
		'dissociation_constant':	0.0
	}
}

model.verify(data)
model.defaults = data
