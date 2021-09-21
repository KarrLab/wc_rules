from .graphs import build_Lyn, build_Syk, build_receptor, recruit_to_receptor, recruit_to_ligand
from .templates import TransPhosphorylationModel

from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.model import AggregateModel

gLynRecruitedDimer = recruit_to_ligand(2,recruit_to_receptor(build_receptor(['alpha','beta']), build_Lyn()))
gReceptorBeta = build_receptor(['alpha','beta'])
gReceptorGamma = build_receptor(['alpha','gamma'])
gReceptorSykLinker = recruit_to_receptor(build_receptor(['alpha','gamma']), build_Syk(['tsh2','linker']))

class LynKinaseModel(TransPhosphorylationModel):

	def __init__(self,target,target_receptor_graph,beta_state):
		g = GraphContainer.compose_from(
			gLynRecruitedDimer.duplicate().set_attr('beta_1','ph',beta_state),
			target_receptor_graph.add_suffix('2'),
		).add_edge('fc_2','bond','alpha_2')
		super().__init__(target,f'{target}_2',g)
		self.verify(self.defaults)

lynstates = [('constitutive',False),('active',False)]
targetpairs = [('beta',gReceptorBeta),('gamma',gReceptorGamma),('linker',gReceptorSykLinker)]

models = []

constitutive_model = AggregateModel(
	name = 'constitutive',
	models = [LynKinaseModel(target,g,beta_state=False) for target,g in targetpairs]
)

active_model = AggregateModel(
	name = 'active',
	models = [LynKinaseModel(target,g,beta_state=True) for target,g in targetpairs]
)

model = AggregateModel(
	name = 'lyn_kinase',
	models = [constitutive_model, active_model]
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