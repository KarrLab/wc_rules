from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.rule import InstanceRateRule
from wc_rules.modeling.model import RuleBasedModel,AggregateModel
from wc_rules.matcher.core import build_rete_net_class
from wc_rules.graph.examples import X,Y
from wc_rules.matcher.token import make_node_token, make_attr_token

import unittest

ReteNet = build_rete_net_class()

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

class ModelInitialization(unittest.TestCase):

	def test_binding_rule(self):
		
		model = AggregateModel('model',models=[BindingRuleModel('binding_model')])
		model_rule_names = [n for n,r in model.iter_rules()]
		self.assertEqual(model_rule_names,['binding_model.binding_rule'])
		model_param_names = [p for p,v in model.iter_parameters()]
		self.assertEqual(model_param_names,['binding_model.k'])
		model.verify(data={'binding_model':{'k':1}})
		
		rn = ReteNet().initialize_start().initialize_end()
		rn.initialize_rules(dict(model.iter_rules()),{'binding_model.k':1})
		self.assertTrue(rn.get_node(core='binding_model.binding_rule.propensity') is not None)
		self.assertTrue(rn.get_node(core='binding_model.k') is not None)
		self.assertTrue(rn.get_channel(
			source = 'binding_model.k',
			target = 'binding_model.binding_rule.propensity',
			type = 'variable_update'
			) is not None)
		reactants = model.models[0].rules[0].reactants.values()
		for pattern in reactants:
			self.assertTrue(rn.get_channel(
				source = pattern,
				target = 'binding_model.binding_rule.propensity',
				type = 'variable_update'
				) is not None)
		self.assertTrue(rn.get_channel(
			source = 'binding_model.binding_rule.propensity',
			target = 'end',
			type = 'variable_update'
			) is not None)

class ModelBehavior(unittest.TestCase):

	def test_binding_rule(self):

		model = AggregateModel('model',models=[BindingRuleModel('binding_model')])
		rn = ReteNet().initialize_start().initialize_end()
		rn.initialize_rules(dict(model.iter_rules()),{'binding_model.k':1})
		start,end = [rn.get_node(type=x) for x in ['start','end',]]
		prop = rn.get_node(core='binding_model.binding_rule.propensity')

		x1,y1 = X('x1'),Y('y1')
		self.assertEqual(prop.state.cache.value,0)
		self.assertEqual(len(end.state.cache),0)

		tokens = [
			make_node_token(X,x1,'AddNode'),
			make_node_token(Y,y1,'AddNode'),
		]
		start.state.incoming.extend(tokens)
		rn.sync(start)
		self.assertEqual(prop.state.cache.value,1)
		self.assertEqual(len(end.state.cache),1)

		x1.y.add(y1)
		tokens = [
			make_attr_token(X,x1,'y','SetAttr'),
			make_attr_token(Y,y1,'x','SetAttr')
		]

		start.state.incoming.extend(tokens)
		rn.sync(start)
		self.assertEqual(prop.state.cache.value,0)
		self.assertEqual(len(end.state.cache),2)
		
		
		
