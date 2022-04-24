import random
random.seed(0)
import sys
from pathlib import Path

from wc_rules.simulator.simulator import SimulationEngine
from wc_rules.modeling.utils import add_models_folder
from wc_rules.modeling.model import AggregateModel
from wc_rules.graph.collections import GraphContainer, MoleculeType, MoleculeInitialization
from wc_rules.simulator.scheduler import RepeatedEventScheduler, CoordinatedScheduler, NextReactionMethod

import unittest

#add_models_folder('/codebase/wc_rules/examples/')
path = Path(__file__).resolve().parent.parent.parent / 'examples'
sys.path.append(str(path))

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


		x1 = X('x1',y=Y('y1'))
		sim.load([GraphContainer(x1.get_connected())])

		self.assertEqual(len(sim.cache),2)
		self.assertEqual(len(px_cache),0)
		self.assertEqual(len(py_cache),0)
		self.assertEqual(len(pxy_cache),1)
		self.assertEqual(sim.get_updated_variables(),sorted([
			'binding_model.binding_rule.propensity',
			'binding_model.unbinding_rule.propensity',
			]))

	def test_load_molecule_initialization(self):
		sim = self.sim
		x1 = X('x1',y=Y('y1'))
		g = MoleculeType(x1.get_connected())
		mm = MoleculeInitialization([(g,2)])
		sim.load([mm])

		px_cache, py_cache = sim.net.get_node(core='binding_model.binding_rule.propensity').data.caches.values()
		pxy_cache = list(sim.net.get_node(core='binding_model.unbinding_rule.propensity').data.caches.values())[0]
		self.assertEqual(len(sim.cache),4)
		self.assertEqual(len(px_cache),0)
		self.assertEqual(len(py_cache),0)
		self.assertEqual(len(pxy_cache),2)


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

		x1 = X('x1',y=Y('y1'))
		sim.load([GraphContainer(x1.get_connected())])
		self.assertEqual(get_lengths([px,py,pxy]),[0,0,1])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[0,1])
		self.assertEqual(sim.get_updated_variables(),variables)

		sim.fire('binding_model.unbinding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,1,0])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[1,0])
		self.assertEqual(sim.get_updated_variables(),variables)

		sim.fire('binding_model.binding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[0,0,1])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[0,1])
		self.assertEqual(sim.get_updated_variables(),variables)

		sim.fire('binding_model.unbinding_rule')
		self.assertEqual(get_lengths([px,py,pxy]),[1,1,0])
		self.assertEqual([prop_binding.value,prop_unbinding.value],[1,0])
		self.assertEqual(sim.get_updated_variables(),variables)

		with self.assertRaises(Exception):
			sim.fire('binding_model.unbinding_rule')

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
		

class TestScheduler(unittest.TestCase):

	def test_coordinated_scheduler(self):
		events = []
		sch1 = RepeatedEventScheduler('read',period=0.25,start=0.0)
		sch2 = RepeatedEventScheduler('write',period=0.5,start=0.0)
		sch3 = CoordinatedScheduler([sch1,sch2])

		while True:
			event, time = sch3.pop()
			if time <= 2:
				events.append((event,time))
			else:
				break

		self.assertEqual(events,[
				('read', 0.0),
				('write', 0.0),
				('read', 0.25),
				('read', 0.5),
				('write', 0.5),
				('read', 0.75),
				('read', 1.0),
				('write', 1.0),
				('read', 1.25),
				('read', 1.5),
				('write', 1.5),
				('read', 1.75),
				('read', 2.0),
				('write', 2.0),
			])

	def test_next_reaction_method(self):
		random.seed(0)

		events = []
		nrm = NextReactionMethod()
		nrm.update(time=0,variables=
			{
			'event01.propensity': 1.0,
			'event02.propensity': 2.0,
			'event03.propensity': 3.0,
		})

		time = 0
		while True:
			event, time = nrm.pop()
			events.append((event,time))
			if time > 2:
				break

		self.assertEqual(events,[
			('event02', 0.13856602479071722),
			('event01', 0.16910308517481865),
			('event03', 0.28871352871962885),
			('event03', 0.5900571449461188),
			('event03', 0.6712582094054508),
			('event02', 0.8141903729866008),
			('event01', 0.8399513032137732),
			('event03', 1.0689218448889979),
			('event03', 1.1010507066243125),
			('event02', 1.1847324255475482),
			('event03', 1.328989749801264),
			('event01', 1.3788643112234498),
			('event03', 1.4223140583199714),
			('event02', 1.8179441221928245),
			('event01', 1.8595342289315115),
			('event02', 1.8652389011676096),
			('event01', 1.8768986455222885),
			('event03', 1.8837377396391415),
			('event02', 1.9704653385098465),
			('event01', 1.9798554408324562),
			('event01', 2.0865075814254235)
			])

		nrm.update(time=0,variables=
			{
			'event02.propensity': 0.0,
			'event03.propensity': 0.0,
			})
		events = []
		while True:
			event, time = nrm.pop()
			events.append((event,time))
			if time > 4:
				break

		self.assertEqual(events,[
			('event01', 2.46632843441263),
			('event01', 3.3006433234303265),
			('event01', 3.7934866465332795),
			('event01', 3.8844939384900092),
			('event01', 3.91845787027947),
			('event01', 4.6586761626656585)
			])