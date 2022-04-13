from wc_rules.graph.examples import X,Y
from wc_rules.modeling.model import RuleBasedModel,AggregateModel
from wc_rules.modeling.pattern import Pattern,GraphContainer
from wc_rules.modeling.rule import InstanceRateRule

class BindingRuleModel(RuleBasedModel):
	defaults = {'k':1}

	def __init__(self,name):
		px = Pattern(GraphContainer([X('x')]))
		py = Pattern(GraphContainer([Y('y')]),constraints = ['len(y.x)==0'])
		rule = InstanceRateRule('binding_rule',
			reactants = {'rX':px, 'rY':py},
			actions = ['rX.x.add_y(rY.y)'],
			rate_prefix = 'k',
			parameters = ['k']
		)
		super().__init__(name=name,rules=[rule])


model = BindingRuleModel('binding_model')
model.verify({'k':1})