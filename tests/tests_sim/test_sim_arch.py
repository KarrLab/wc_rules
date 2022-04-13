from wc_rules.simulator.simulator import Simulator
from wc_rules.modeling.utils import add_models_folder
from wc_rules.modeling.model import AggregateModel

import unittest

add_models_folder('/codebase/wc_rules/examples/')

from simple_binding_reaction.model import model as simple_binding_reaction_model

class TestSimpleBindingModel(unittest.TestCase):

	def setUp(self):
		self.model =  AggregateModel('binding_model',models=[simple_binding_reaction_model])
		self.data = {'binding_model':{'k':1}}	

	def test_data_verify(self):
		self.model.verify(self.data)
		
	def test_init_simulator(self):
		model,params = self.model,self.data
		
		sim = Simulator(model=model,parameters=params)

		for name,rule in sim.rules.items():
			self.assertTrue(sim.net.get_node(core=f'{name}.propensity') is not None)
			for p in rule.parameters:
				p1 = '.'.join(name.split('.')[:-1]) + f'.{p}'
				self.assertTrue(p1 in sim.parameters)
				self.assertTrue(p1 in sim.parameter_dependencies[name])
