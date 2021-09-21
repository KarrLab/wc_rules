from .templates import DephosphorylationModel
from .graphs import build_receptor, build_Syk, recruit_to_receptor, add_phosphosite_to_molecule

from wc_rules.modeling.pattern import Pattern
from wc_rules.modeling.model import AggregateModel

gRecPhospho = add_phosphosite_to_molecule(build_receptor([]),'receptor')
gFreeSykPhospho = add_phosphosite_to_molecule(build_Syk([]),'syk')
gMembraneSykPhospho = recruit_to_receptor(build_receptor(['gamma']), add_phosphosite_to_molecule(build_Syk(['tsh2']),'syk'))

model = AggregateModel(
	name = 'dephosphorylation',
	models = [ 
		DephosphorylationModel('receptor',gRecPhospho),
		DephosphorylationModel('membrane_syk',gMembraneSykPhospho),
		DephosphorylationModel('free_syk',gFreeSykPhospho),
		]
	)

data = {
	'receptor': 	{'dephosphorylation_rate': 20.0},
	'membrane_syk': {'dephosphorylation_rate': 20.0},
	'free_syk':		{'dephosphorylation_rate': 20.0}
}

model.verify(data)
model.defaults = data
