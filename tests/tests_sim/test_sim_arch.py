from wc_rules.simulator.simulator import SimulationEngine
from wc_rules.modeling.utils import add_models_folder
from wc_rules.modeling.model import AggregateModel
from wc_rules.graph.collections import GraphContainer

import unittest

add_models_folder('/codebase/wc_rules/examples/')

from simple_binding.model import model as simple_binding_model
from simple_binding.model import X,Y
from simple_flip.model import model as flip_model
from simple_flip.model import Point

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
		sim = self.sim
		self.assertTrue(sim.net.get_node(core='binding_model.binding_rule.propensity') is not None)
		self.assertTrue(sim.net.get_node(core='binding_model.unbinding_rule.propensity') is not None)
		self.assertTrue('binding_model.kf' in sim.parameters)
		self.assertTrue('binding_model.kr' in sim.parameters)


	def test_load(self):
		sim = self.sim
		px_cache, py_cache = sim.net.get_node(core='binding_model.binding_rule.propensity').data.caches.values()
		pxy_cache = list(sim.net.get_node(core='binding_model.unbinding_rule.propensity').data.caches.values())[0]

		self.assertEqual(len(sim.cache),0)
		self.assertEqual(len(px_cache),0)
		self.assertEqual(len(py_cache),0)
		self.assertEqual(len(pxy_cache),0)
		self.assertEqual(sim.get_updated_variables(),sorted([
			'binding_model.binding_rule.propensity',
			'binding_model.unbinding_rule.propensity',
			'binding_model.kf',
			'binding_model.kr',
			]))


		x1 = X('x1',y=[Y('y1'), Y('y2')])
		sim.load([GraphContainer(x1.get_connected())])

		self.assertEqual(len(sim.cache),3)
		self.assertEqual(len(px_cache),1)
		self.assertEqual(len(py_cache),0)
		self.assertEqual(len(pxy_cache),2)
		self.assertEqual(sim.get_updated_variables(),sorted([
			'binding_model.binding_rule.propensity',
			'binding_model.unbinding_rule.propensity',
			]))


	def test_fire(self):
		sim = self.sim
		names = [f'binding_model.{x}_rule.propensity' for x in ['binding','unbinding']]
		n_binding,n_unbinding = [sim.net.get_node(core=x) for x in names]
		px, py = n_binding.data.caches.values()
		pxy = list(n_unbinding.data.caches.values())[0]
		prop_binding = n_binding.state.cache
		prop_unbinding = n_unbinding.state.cache
		variables = [f'binding_model.{x}binding_rule.propensity' for x in ['','un']]

		self.assertEqual(prop_binding.value,prop_unbinding.value,[0,0])
		with self.assertRaises(Exception):
			sim.fire('binding_model.unbinding_rule')

		self.assertEqual(sim.get_updated_variables(),sorted([
			'binding_model.binding_rule.propensity',
			'binding_model.unbinding_rule.propensity',
			'binding_model.kf',
			'binding_model.kr',
			]))

		x1 = X('x1',y=[Y('y1'), Y('y2')])
		sim.load([GraphContainer(x1.get_connected())])
		self.assertEqual(get_lengths([px,py,pxy]),[1,0,2])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[0,2])
		self.assertEqual(sim.get_updated_variables(),variables)

		sim.fire('binding_model.unbinding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,1,1])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[1,1])
		self.assertEqual(sim.get_updated_variables(),variables)

		sim.fire('binding_model.unbinding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,2,0])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[2,0])
		self.assertEqual(sim.get_updated_variables(),variables)

		sim.fire('binding_model.binding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,1,1])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[1,1])
		self.assertEqual(sim.get_updated_variables(),variables)

		sim.fire('binding_model.binding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,0,2])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[0,2])
		self.assertEqual(sim.get_updated_variables(),variables)

		with self.assertRaises(Exception):
			sim.fire('binding_model.binding_rule')

class TestFlipModel(unittest.TestCase):
	# note that the pattern used here is symmetric, 
	# so test multiple ways to load

	def setUp(self):
		self.model =  AggregateModel('model',models=[flip_model])
		self.data = {'flip_model':{'k':1}}
		self.sim = SimulationEngine(model=self.model,parameters=self.data)

	def test_data_verify(self):
		self.model.verify(self.data)
	
	def test_init_simulator(self):
		sim = self.sim
		self.assertTrue(sim.net.get_node(core='flip_model.flipping_rule.propensity') is not None)
		self.assertTrue('flip_model.k' in sim.parameters)
		
	def test_load1(self):
		sim = self.sim
		s = sim.cache
		g = sim.net.get_node(type='canonical_label').state.cache
		p = sim.net.get_node(core='flip_model.flipping_rule.propensity').data.caches['rXX']
		self.assertEqual(get_lengths([s,g,p]),[0,0,0])
		self.assertEqual(sim.get_updated_variables(),sorted([
			'flip_model.flipping_rule.propensity',
			'flip_model.k',
			]))


		x1 = Point('x1',v=False,points=[Point('x2',v=False)])
		sim.load([GraphContainer(x1.get_connected())])
		self.assertEqual(get_lengths([s,g,p]),[2,2,0])
		self.assertEqual(sim.get_updated_variables(),[])

		
	def test_load2(self):
		sim = self.sim
		s = sim.cache
		g = sim.net.get_node(type='canonical_label').state.cache
		p = sim.net.get_node(core='flip_model.flipping_rule.propensity').data.caches['rXX']
		self.assertEqual(get_lengths([s,g,p]),[0,0,0])
		self.assertEqual(sim.get_updated_variables(),sorted([
			'flip_model.flipping_rule.propensity',
			'flip_model.k',
			]))

		x1 = Point('x1',v=True,points=[Point('x2',v=False)])
		sim.load([GraphContainer(x1.get_connected())])
		self.assertEqual(get_lengths([s,g,p]),[2,2,1])
		self.assertEqual(p.filter()[0],{'x_on':s['x1'],'x_off':s['x2']})
		self.assertEqual(sim.get_updated_variables(),['flip_model.flipping_rule.propensity'])

		
	def test_load3(self):
		sim = self.sim
		s = sim.cache
		g = sim.net.get_node(type='canonical_label').state.cache
		p = sim.net.get_node(core='flip_model.flipping_rule.propensity').data.caches['rXX']
		self.assertEqual(get_lengths([s,g,p]),[0,0,0])
		self.assertEqual(sim.get_updated_variables(),sorted([
			'flip_model.flipping_rule.propensity',
			'flip_model.k',
			]))

		x1 = Point('x1',v=False,points=[Point('x2',v=True)])
		sim.load([GraphContainer(x1.get_connected())])
		self.assertEqual(get_lengths([s,g,p]),[2,2,1])
		self.assertEqual(p.filter()[0],{'x_on':s['x2'],'x_off':s['x1']})
		self.assertEqual(sim.get_updated_variables(),['flip_model.flipping_rule.propensity'])
		

	def test_fire(self):
		sim = self.sim
		g = sim.net.get_node(type='canonical_label').state.cache
		p = sim.net.get_node(core='flip_model.flipping_rule.propensity').data.caches['rXX']
		prop = sim.net.get_node(core='flip_model.flipping_rule.propensity').state.cache
		self.assertEqual(sim.get_updated_variables(),sorted([
			'flip_model.flipping_rule.propensity',
			'flip_model.k',
			]))

		self.assertEqual([g.count(),p.count(),prop.value],[0,0,0])
		with self.assertRaises(Exception):
			sim.fire('flip_model.flipping_rule')

		x1 = Point('x1',v=False,points=[Point('x2',v=True)])
		sim.load([GraphContainer(x1.get_connected())])
		self.assertEqual([g.count(),p.count(),prop.value],[2,1,1])
		self.assertEqual([sim.cache[x].v for x in ['x1','x2']],[False,True])
		self.assertEqual(sim.get_updated_variables(),['flip_model.flipping_rule.propensity'])
		
		sim.fire('flip_model.flipping_rule')
		self.assertEqual([g.count(),p.count(),prop.value],[2,1,1])
		self.assertEqual([sim.cache[x].v for x in ['x1','x2']],[True,False])
		self.assertEqual(sim.get_updated_variables(),['flip_model.flipping_rule.propensity'])
			
		sim.fire('flip_model.flipping_rule')
		self.assertEqual([g.count(),p.count(),prop.value],[2,1,1])
		self.assertEqual([sim.cache[x].v for x in ['x1','x2']],[False,True])
		self.assertEqual(sim.get_updated_variables(),['flip_model.flipping_rule.propensity'])
		