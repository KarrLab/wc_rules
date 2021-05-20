from ..templates.graphs import *
from ..templates.rules import *
from wc_rules.modeling.pattern import Pattern
from wc_rules.modeling.model import AggregateModel

def build_model(aloop=False):
	state = {True:'phosphorylated',False:'unphosphorylated'}
	return TransPhosphorylationModel(
		name = f'aloop_{state[aloop]}',
		reactant = Pattern(gSykOnSyk, constraints = [f'aloop_left.ph == {aloop}', f'aloop_right.ph == False']),
		target = 'aloop_right',
	)

model = AggregateModel(
	name = 'syk_kinase',
	models = [
		build_model(aloop=False),
		build_model(aloop=True)	
	]
)

data =	{
	'aloop_unphosphorylated': 	{'phosphorylation_rate': 100},
	'aloop_phosphorylated': 	{'phosphorylation_rate': 200},
}

model.verify(data)
model.defaults = data