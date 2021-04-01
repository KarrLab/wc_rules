
from wc_rules.pattern import Pattern
from wc_rules.model import AggregateModel
from template_molecular_graphs import *
from template_rules import BindingModel


# Pattern template
def build_ligand_pattern(v1,v2):
	constraints = [f'len(fc1.bond) == {v1}',f'len(fc2.bond) == {v2}']
	return Pattern(gLigand,constraints=constraints)

# Patterns
free_ligand = build_ligand_pattern(0,0)
singly_bound_ligand = build_ligand_pattern(1,0)
doubly_bound_ligand = build_ligand_pattern(1,1)
free_receptor = Pattern(gReceptorAlpha,constraints = ['len(alpha.bond) == 0'])

# RuleBasedModels
monomer_inputs = [ 
	('free_ligand',free_ligand,'fc1'), 
	('free_receptor',free_receptor,'alpha'),
	('singly_bound_ligand',singly_bound_ligand,'fc1')
	]
monomer_model = BindingModel('monomer',monomer_inputs )

dimer_inputs = [
	('singly_bound_ligand',singly_bound_ligand,'fc2'), 
	('free_receptor',free_receptor,'alpha'),
	('doubly_bound_ligand',doubly_bound_ligand,'fc2')
	]
dimer_model = BindingModel('dimer',dimer_inputs)


# Aggregate model
model = AggregateModel(
	name = 'ligand_receptor',
	models = [ monomer_model, dimer_model]
	)

# setting default parameters
data = {
	'monomer':{'association_constant':1.3e-7, 'dissociation_constant':0.0},
	'dimer':{'association_constant':2.5e-1, 'dissociation_constant':0.0}
}

model.verify(data)
model.defaults = data
