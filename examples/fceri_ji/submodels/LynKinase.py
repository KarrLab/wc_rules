from ..templates.graphs import *
from ..templates.rules import *
from wc_rules.modeling.pattern import Pattern
from wc_rules.modeling.model import AggregateModel

def build_model(target,g,active=False):
	return TransPhosphorylationModel(
		name = target,
		reactant = Pattern(g, constraints = [f'beta_left.ph == {active}', f'{target}_right.ph == False']),
		target = f'{target}_right',
	)

transph_configurations = {
	'beta': 	gLynOnBeta,
	'gamma': 	gLynOnGamma,
	'linker':	gLynOnSykLinker
}

constitutive_lyn_kinase = AggregateModel(
	name = 'constitutive',
	models = [build_model(target,g,False) for target,g in transph_configurations.items()]
)

active_lyn_kinase = AggregateModel(
	name = 'active',
	models = [build_model(target,g,True) for target,g in transph_configurations.items()]
)

model = AggregateModel(
	name = 'lyn_kinase',
	models = [
		constitutive_lyn_kinase,
		active_lyn_kinase
	]
)

data = {
	'constitutive':{
		'beta': 	{'phosphorylation_rate': 30},
		'gamma': 	{'phosphorylation_rate': 1},
		'linker': 	{'phosphorylation_rate': 30}
	},
	'active': {
		'beta': 	{'phosphorylation_rate': 100},
		'gamma': 	{'phosphorylation_rate': 3},
		'linker': 	{'phosphorylation_rate': 100}
	}
}
model.verify(data)
model.defaults = data