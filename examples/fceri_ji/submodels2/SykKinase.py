from .graphs import build_Syk, build_receptor, recruit_to_receptor, recruit_to_ligand
from .templates import TransPhosphorylationModel

from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.model import AggregateModel

gRecSyk = recruit_to_receptor(build_receptor(['alpha','gamma']), build_Syk(['tsh2','aloop']))
gSykOnSyk = recruit_to_ligand(2,gRecSyk,gRecSyk.duplicate())

class SykKinaseModel(TransPhosphorylationModel):

	def __init__(self,name,aloop_state):
		g = Pattern(gSykOnSyk, constraints = [f'aloop_1.ph == {aloop_state}'])
		super().__init__(name,'aloop_2',g)
		self.verify(self.defaults)


model = AggregateModel(
	name = 'syk_kinase',
	models = [
		SykKinaseModel(name='aloop_unphosphorylated',aloop_state=False),
		SykKinaseModel(name='aloop_phosphorylated',aloop_state=True)
	]
)

data =	{
	'aloop_unphosphorylated': 	{'phosphorylation_rate': 100},
	'aloop_phosphorylated': 	{'phosphorylation_rate': 200},
}

model.verify(data)
model.defaults = data

