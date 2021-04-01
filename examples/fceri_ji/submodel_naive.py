######## "No templated rules" version #########

from template_molecular_graphs import gLigand, gReceptorAlpha
from wc_rules.pattern import Pattern
from wc_rules.rule import Rule
from wc_rules.model import RuleBasedModel, AggregateModel

free_ligand = Pattern(
	parent = gLigand,
	constraints = ['len(fc1.bond)==0', 'len(fc2.bond)==0']
	)

singly_bound_ligand = Pattern(
	parent = gLigand,
	constraints = ['len(fc1.bond)==1', 'len(fc2.bond)==0']
	)

doubly_bound_ligand = Pattern(
	parent = gLigand,
	constraints = ['len(fc1.bond)==1', 'len(fc2.bond)==1']
	)

free_receptor = Pattern(
	parent = gReceptorAlpha,
	constraints = ['len(alpha.bond)==0']
	)

# Monomer model
monomer_binding_rule = Rule(
	name = 'monomer_binding_rule',
	reactants = {'ligand_reactant': free_ligand, 'free_receptor': free_receptor},
	actions = ['ligand_reactant.fc1.add_bond(free_receptor.alpha)'],
	rate_prefix = 'association_constant',
	params = ['association_constant']
	)

monomer_unbinding_rule = Rule(
	name = 'monomer_unbinding_rule',
	reactants = {'ligand_reactant': singly_bound_ligand},
	actions = ['ligand_reactant.fc1.remove_bond()'],
	rate_prefix = 'dissociation_constant',
	params = ['dissociation_constant']
	)

monomer_ligand_model = RuleBasedModel(
	name = 'monomer_ligand',
	rules = [monomer_binding_rule, monomer_unbinding_rule]
	)

# Dimer model
dimer_binding_rule = Rule(
	name = 'dimer_binding_rule',
	reactants = {'ligand_reactant': singly_bound_ligand, 'free_receptor': free_receptor},
	actions = ['ligand_reactant.fc2.add_bond(free_receptor.alpha)'],
	rate_prefix = 'association_constant',
	params = ['association_constant']
	)

dimer_unbinding_rule = Rule(
	name = 'dimer_unbinding_rule',
	reactants = {'ligand_reactant':doubly_bound_ligand},
	actions = ['ligand_reactant.fc1.remove_bond()'],
	rate_prefix = 'dissociation_constant',
	params = ['dissociation_constant']
	)

dimer_ligand_model = RuleBasedModel(
	name = 'dimer_ligand',
	rules = [dimer_binding_rule, dimer_unbinding_rule]
	)

# Aggregate Model
model = AggregateModel(
	name = 'ligand_receptor_binding',
	models = [monomer_ligand_model, dimer_ligand_model]
	)
model.defaults = 


data = {
	'monomer_ligand': {
		'association_constant' : 1.3e-7,
		'dissociation_constant': 0.0,
	},
	'dimer_ligand': {
		'association_constant' : 2.5e-1,
		'dissociation_constant': 0,
	}
}

model.verify(data)
