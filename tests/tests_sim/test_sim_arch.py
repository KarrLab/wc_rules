from wc_rules.simulator.simulator import SimulationEngine
from wc_rules.modeling.utils import add_models_folder
from wc_rules.modeling.model import AggregateModel
from wc_rules.graph.collections import GraphContainer

import unittest

add_models_folder('/codebase/wc_rules/examples/')

from simple_binding.model import model as simple_binding_model
from simple_binding.model import X,Y

def get_lengths(elems):
	return list(map(len,elems))

class TestSimpleBindingModel(unittest.TestCase):

	def setUp(self):
		self.model =  AggregateModel('model',models=[simple_binding_model])
		self.data = {'binding_model':{'kf':1,'kr':1}}
		self.sim = SimulationEngine(model=self.model,parameters=self.data)

	def test_data_verify(self):
		self.model.verify(self.data)
		
	def test_init_simulator(self):
		#model,params = self.model,self.data
	
		# sim = self.sim
		# for name,rule in sim.rules.items():
		# 	self.assertTrue(sim.net.get_node(core=f'{name}.propensity') is not None)
		# 	for p in rule.parameters:
		# 		p1 = '.'.join(name.split('.')[:-1]) + f'.{p}'
		# 		self.assertTrue(p1 in sim.parameters)
		# 		self.assertTrue(p1 in sim.parameter_dependencies[name])
		sim = self.sim
		self.assertTrue(sim.net.get_node(core='binding_model.binding_rule.propensity') is not None)
		self.assertTrue(sim.net.get_node(core='binding_model.unbinding_rule.propensity') is not None)
		self.assertTrue('binding_model.kf' in sim.parameters)
		self.assertTrue('binding_model.kr' in sim.parameters)
		self.assertEqual(dict(sim.parameter_dependencies),{
			'binding_model.binding_rule':['binding_model.kf'],
			'binding_model.unbinding_rule':['binding_model.kr'],
		})


	def test_load(self):
		sim = self.sim
		px_cache, py_cache = sim.net.get_node(core='binding_model.binding_rule.propensity').data.caches.values()
		pxy_cache = list(sim.net.get_node(core='binding_model.unbinding_rule.propensity').data.caches.values())[0]

		self.assertEqual(len(sim.cache),0)
		self.assertEqual(len(px_cache),0)
		self.assertEqual(len(py_cache),0)
		self.assertEqual(len(pxy_cache),0)


		x1 = X('x1',y=[Y('y1'), Y('y2')])
		sim.load([GraphContainer(x1.get_connected())])

		self.assertEqual(len(sim.cache),3)
		self.assertEqual(len(px_cache),1)
		self.assertEqual(len(py_cache),0)
		self.assertEqual(len(pxy_cache),2)

	def test_fire(self):
		sim = self.sim
		px, py = sim.net.get_node(core='binding_model.binding_rule.propensity').data.caches.values()
		pxy = list(sim.net.get_node(core='binding_model.unbinding_rule.propensity').data.caches.values())[0]

		with self.assertRaises(Exception):
			sim.fire('binding_model.unbinding_rule')

		x1 = X('x1',y=[Y('y1'), Y('y2')])
		sim.load([GraphContainer(x1.get_connected())])
		self.assertEqual(get_lengths([px,py,pxy]),[1,0,2])

		sim.fire('binding_model.unbinding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,1,1])

		sim.fire('binding_model.unbinding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,2,0])

		sim.fire('binding_model.binding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,1,1])

		sim.fire('binding_model.binding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,0,2])

		with self.assertRaises(Exception):
			sim.fire('binding_model.binding_rule')