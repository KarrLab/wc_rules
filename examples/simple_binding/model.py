from wc_rules.schema.entity import Entity
from wc_rules.schema.attributes import *
from wc_rules.modeling.model import RuleBasedModel,AggregateModel
from wc_rules.modeling.pattern import Pattern,GraphContainer, SimpleObservable
from wc_rules.modeling.rule import InstanceRateRule
from wc_rules.utils.data import DataFileUtil

class X(Entity):
	pass

class Y(Entity):
	x = OneToOneAttribute(X,related_name='y')

class SimpleBindingModel(RuleBasedModel):
	defaults = {'kf':1,'kr':1}

	def __init__(self,name):
		px = Pattern(GraphContainer([X('x')]),constraints = ['len(x.y)==0'])
		py = Pattern(GraphContainer([Y('y')]),constraints = ['len(y.x)==0'])
		pxy = Pattern(GraphContainer(X('x',y=Y('y')).get_connected()))

		rule1 = InstanceRateRule('binding_rule',
			reactants = {'rX':px, 'rY':py},
			actions = ['rX.x.add_y(rY.y)'],
			rate_prefix = 'kf',
			parameters = ['kf']
		)

		rule2 = InstanceRateRule('unbinding_rule',
			reactants = {'rXY':pxy},
			actions = ['rXY.x.remove_y(rXY.y)'],
			rate_prefix = 'kr',
			parameters = ['kr']
		)
		observables = [SimpleObservable(name,target) for name,target in {'x':px,'y':py,'xy':pxy}.items()]
		super().__init__(name=name,rules=[rule1,rule2],observables=observables)


model = SimpleBindingModel('binding_model')
model.verify({'kf':1,'kr':1})
