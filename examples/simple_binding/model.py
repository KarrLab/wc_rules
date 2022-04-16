from wc_rules.graph.examples import X,Y
from wc_rules.modeling.model import RuleBasedModel,AggregateModel
from wc_rules.modeling.pattern import Pattern,GraphContainer
from wc_rules.modeling.rule import InstanceRateRule

class SimpleBindingModel(RuleBasedModel):
	defaults = {'kf':1,'kr':1}

	def __init__(self,name):
		px = Pattern(GraphContainer([X('x')]))
		py = Pattern(GraphContainer([Y('y')]),constraints = ['len(y.x)==0'])
		pxy = Pattern(GraphContainer(X('x',y=[Y('y')]).get_connected()))

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
		super().__init__(name=name,rules=[rule1,rule2])


model = SimpleBindingModel('binding_model')
model.verify({'kf':1,'kr':1})