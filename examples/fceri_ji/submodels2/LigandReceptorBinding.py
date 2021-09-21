
from .graphs import build_ligand, build_receptor, recruit_to_receptor, recruit_to_ligand
from .templates import BindingModel

from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.model import AggregateModel

gFc = build_ligand(1)
gAlpha = build_receptor(['alpha'])
gFcAlphaBond = recruit_to_ligand(1,build_receptor(['alpha']))
gRecruitedLigandContext = recruit_to_ligand(2,build_receptor(['alpha']))

class LigandBindingModel(BindingModel):
	
	def __init__(self,name,recruitedBool):
		helpers = {'recruited_context':Pattern(gRecruitedLigandContext)}
		constraints = [f'recruited_context.contains(fc=fc)=={recruitedBool}']
		pLigand = Pattern(parent=gFc, helpers=helpers, constraints=constraints)
		pBoundLigand = Pattern(parent=gFcAlphaBond, helpers=helpers, constraints=constraints)
		reactants = {
			'rLigand': pLigand,
			'rReceptor':gAlpha,
			'rBoundLigand': pBoundLigand
		}
		targets = ['fc','alpha']
		super().__init__(name,reactants,targets)


	
model = AggregateModel(name = 'ligand_receptor', models = 
	[
		LigandBindingModel(name = 'monomer', recruitedBool=False),
		LigandBindingModel(name = 'dimer', recruitedBool=True),
	]
)

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
