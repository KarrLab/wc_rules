from wc_rules.simulator.simulator import Simulator
from wc_rules.modeling.utils import add_models_folder
from wc_rules.modeling.model import AggregateModel

import unittest

add_models_folder('/codebase/wc_rules/examples/')

from simple_binding_reaction.model import model

class TestSimpleBindingModel(unittest.TestCase):

	def test_data_verify(self):
		model.verify({'k':1})
		params = {'binding_model':{'k':1}}
		AggregateModel('binding_model',models=[model]).verify(params)

	def test_init_simulator(self):
		params = {'binding_model':{'k':1}}
		sim = Simulator(model=model,parameters=params)

		for name,rule in sim.model.iter_rules():
			self.assertTrue(sim.net.get_node(core=f'{name}.propensity') is not None)

		for name,pattern in sim.model.iter_parameters():
			self.assertTrue(sim.net.get_node(core=name) is not None)
