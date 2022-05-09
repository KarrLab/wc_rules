from wc_rules.schema.entity import Entity
from wc_rules.graph.collections import GraphContainer, GraphFactory
from wc_rules.modeling.pattern import Pattern,SimpleObservable
from wc_rules.modeling.rule import InstanceRateRule
from wc_rules.modeling.model import RuleBasedModel

class X(Entity):
	pass

class Y(Entity):
	pass

class Z(Entity):
	pass

class SimpleAddRemoveModel(RuleBasedModel):

	data = {'k1':1,'k2':1,'k3':1,'k4':1}

	def __init__(self,name):
		gx,gy,gz = [GraphFactory([C(c)]) for C,c in [(X,'x'),(Y,'y'),(Z,'z')]]
		px,py,pz = [Pattern(x) for x in [gx,gy,gz]]

		r1 = InstanceRateRule(
			name = 'adding_x',
			factories = {'px':gx},
			actions = ['add(px)'],
			rate_prefix = 'k1',
			parameters = ['k1']
			)

		r2 = InstanceRateRule(
			name = 'adding_y',
			factories = {'py':gy},
			actions = ['add(py)'],
			rate_prefix = 'k2',
			parameters = ['k2']
			)

		r3 = InstanceRateRule(
			name = 'transforming_xy_to_z',
			reactants = {'px':px,'py':py},
			factories = {'pz':gz},
			actions = ['remove(px)','remove(py)','add(pz)'],
			rate_prefix = 'k3',
			parameters = ['k3']
			)

		r4 = InstanceRateRule(
			name = 'removing_z',
			reactants = {'pz':pz,},
			actions = ['remove(pz)'],
			rate_prefix = 'k4',
			parameters = ['k4']
			)

		obs1 = SimpleObservable(name='x',target=pz)
		obs2 = SimpleObservable(name='y',target=pz)
		obs3 = SimpleObservable(name='z',target=pz)

		super().__init__(name,rules=[r1,r2,r3,r4],observables=[obs1,obs2,obs3])

# model = RuleBasedModel('addremove_model',rules=[r1,r2,r3,r4])
model = SimpleAddRemoveModel('addremove_model')

