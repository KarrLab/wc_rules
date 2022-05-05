from wc_rules.schema.entity import Entity
from wc_rules.graph.collections import GraphContainer, MoleculeType
from wc_rules.modeling.pattern import GraphContainer,Pattern,Observable
from wc_rules.modeling.rule import InstanceRateRule
from wc_rules.modeling.model import RuleBasedModel

class X(Entity):
	pass

class Y(Entity):
	pass

class Z(Entity):
	pass

gx,gy,gz = [GraphContainer([C(c)]) for C,c in [(X,'x'),(Y,'y'),(Z,'z')]]
px,py,pz = [Pattern(x) for x in [gx,gy,gz]]
mx,my,mz = [MoleculeType(x) for x in [gx,gy,gz]]

xrule = InstanceRateRule(
	name = 'x_addition_rule',
	helpers = {'px':px},
	actions = ['px.add()'],
	rate_prefix = 'kp',
	parameters = ['kp']
	)

model = RuleBasedModel('addremove_model',rules=[xrule])


