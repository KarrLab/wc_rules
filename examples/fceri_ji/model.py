
from submodel_LigandReceptorBinding import model as ligand_receptor_binding_model
from submodel_LynReceptorBinding import model as lyn_receptor_binding_model
from submodel_SykReceptorBinding import model as syk_receptor_binding_model

from submodel_LynKinase import model as lyn_kinase_model
from submodel_SykKinase import model as syk_kinase_mdoel

from submodel_dephosphorylation import model as dephosphorylation_model

from wc_rules.modeling.model import AggregateModel


binding_model = AggregateModel(
	name = 'binding',
	models = [
		ligand_receptor_binding_model,
		lyn_receptor_binding_model,
		syk_receptor_binding_model
	]
)

transphosphorylation_model = AggregateModel(
	name = 'transphosphorylation',
	models = [
		lyn_kinase_model,
		syk_kinase_mdoel
	]
)

model = AggregateModel(
	name = 'fceri_ji',
	models = [
		binding_model,
		transphosphorylation_model,
		dephosphorylation_model
	]
)
