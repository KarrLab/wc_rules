from wc_rules.schema.entity import Entity
from wc_rules.schema.attributes import BooleanAttribute, ManyToManyAttribute
from wc_rules.modeling.pattern import GraphContainer,Pattern
from wc_rules.modeling.rule import InstanceRateRule
from wc_rules.modeling.model import RuleBasedModel


class Point(Entity):

	points = ManyToManyAttribute('Point',related_name='points')
	v = BooleanAttribute()	

class FlipModel(RuleBasedModel):

	defaults = {'k':1}

	def __init__(self,name):
		gXX = GraphContainer(Point('x_on',v=True,points=[Point('x_off',v=False)]).get_connected())
		rule = InstanceRateRule('flipping_rule',
			reactants = {'rXX': Pattern(gXX)},
			actions = ['rXX.x_on.setFalse_v()','rXX.x_off.setTrue_v()'],
			parameters = ['k'],
			rate_prefix = 'k'
			)

		super().__init__(name,rules=[rule])


model = FlipModel('flip_model')
