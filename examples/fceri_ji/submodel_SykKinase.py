from template_molecular_graphs import *
from template_rules import *
from wc_rules.pattern import Pattern
from wc_rules.model import AggregateModel


pSykALoopFalseOnSyk = Pattern(gSykOnSyk,constraints = ['aloop_left.ph==False','aloop_right.ph==False'])
pSykALoopTrueOnSyk = Pattern(gSykOnSyk,constraints = ['aloop_left.ph==True','aloop_right.ph==False'])

model = AggregateModel(
	name = 'syk_kinase',
	models = [
		TransPhosphorylationModel('syk_aloopfalse_on_syk',pSykALoopFalseOnSyk,'aloop_right'),
		TransPhosphorylationModel('syk_alooptrue_on_syk',pSykALoopTrueOnSyk,'aloop_right')
	]
)

data =	{
	'syk_aloopfalse_on_syk': {'phosphorylation_rate': 100},
	'syk_alooptrue_on_syk': {'phosphorylation_rate': 200},
}
model.verify(data)
model.defaults = data