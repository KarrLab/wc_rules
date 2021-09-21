from .graphs import build_Syk, build_receptor, recruit_to_receptor
from .templates import BindingModel

from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.model import AggregateModel


gTandemSH2 = build_Syk(['tsh2'])
gGamma = build_receptor(['gamma'])
gTandemSH2GammaBond = recruit_to_receptor(build_receptor(['gamma']),build_Syk(['tsh2']))


class SykReceptorBindingModel(BindingModel):

	def __init__(self):
		return super().__init__(
			name = 'syk_receptor',
			reactants = {
				'rTandemSH2':gTandemSH2,
				'rGamma': gGamma,
				'rTandemSH2GammaBond': gTandemSH2GammaBond
			},
			targets = ['tsh2','gamma']
		)

model = SykReceptorBindingModel()

data = {
	'association_constant':		6e-2, 
	'dissociation_constant':	20.0
}

model.verify(data)
model.defaults = data