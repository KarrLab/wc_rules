from wc_rules.base import BaseClass
from wc_rules.attributes import *
from wc_rules.actions import *
from wc_rules.simulator import SimulationState
import unittest


class Animal(BaseClass):
	sound = StringAttribute()
	friends = ManyToManyAttribute('Animal',related_name='friends')

class Person(BaseClass):
	pets = OneToManyAttribute(Animal,related_name='owner')

def string_to_action_object(s,_locals):
	fn = eval('lambda: ' + s,_locals)
	return fn()	


class TestActionObjects(unittest.TestCase):

	def setUp(self):
		self.locals = dict(
			sim = SimulationState(),
			Animal = Animal,
			Person = Person,
			AddNode = AddNode,
			RemoveNode = RemoveNode,
			SetAttr = SetAttr,
			AddEdge = AddEdge,
			RemoveEdge = RemoveEdge
			)

	def test_primary_action_objects(self):

		action_strings = '''
			AddNode.make(Animal,'doggy',dict(sound='ruff'))
			AddNode.make(Animal,'kitty',dict(sound='woof'))
			AddNode.make(Person,'john')
			SetAttr.make(sim.resolve('kitty'),'sound','meow')
			AddEdge.make(sim.resolve('doggy'),'owner',sim.resolve('john'))
			AddEdge.make(sim.resolve('kitty'),'owner',sim.resolve('john'))
			AddEdge.make(sim.resolve('doggy'),'friends',sim.resolve('kitty'))
			RemoveEdge.make(sim.resolve('john'),'pets',sim.resolve('doggy'))
			RemoveEdge.make(sim.resolve('john'),'pets',sim.resolve('kitty'))
			RemoveEdge.make(sim.resolve('kitty'),'friends',sim.resolve('doggy'))
			RemoveNode.make(sim.resolve('john'))
			RemoveNode.make(sim.resolve('doggy'))
			RemoveNode.make(sim.resolve('kitty'))
		'''

		actions = [
			AddNode(Animal,'doggy',{'sound':'ruff'}),
			AddNode(Animal,'kitty',{'sound':'woof'}),
			AddNode(Person,'john',{}),
			SetAttr('kitty','sound','meow','woof'),
			AddEdge('doggy','owner','john','pets'),
			AddEdge('kitty','owner','john','pets'),
			AddEdge('doggy','friends','kitty','friends'),
			RemoveEdge('john','pets','doggy','owner'),
			RemoveEdge('john','pets','kitty','owner'),
			RemoveEdge('kitty','friends','doggy','friends'),
			RemoveNode(Person,'john',{}),
			RemoveNode(Animal,'doggy',{'sound':'ruff'}),
			RemoveNode(Animal,'kitty',{'sound':'meow'}),
		]

		states = [
			{},
			{'doggy': {'sound': 'ruff'}},
			{'doggy': {'sound': 'ruff'}, 'kitty': {'sound': 'woof'}},
			{'doggy': {'sound': 'ruff'}, 'john': {}, 'kitty': {'sound': 'woof'}},
			{'doggy': {'sound': 'ruff'}, 'john': {}, 'kitty': {'sound': 'meow'}},
			{'doggy': {'sound': 'ruff', 'owner': 'john'}, 'john': {'pets': ['doggy']}, 'kitty': {'sound': 'meow'}},
			{'doggy': {'sound': 'ruff', 'owner': 'john'}, 'john': {'pets': ['doggy', 'kitty']}, 'kitty': {'sound': 'meow', 'owner': 'john'}},
			{'doggy': {'sound': 'ruff', 'friends': ['kitty'], 'owner': 'john'}, 'john': {'pets': ['doggy', 'kitty']}, 'kitty': {'sound': 'meow', 'friends': ['doggy'], 'owner': 'john'}},
			{'doggy': {'sound': 'ruff', 'friends': ['kitty']}, 'john': {'pets': ['kitty']}, 'kitty': {'sound': 'meow', 'friends': ['doggy'], 'owner': 'john'}},
			{'doggy': {'sound': 'ruff', 'friends': ['kitty']}, 'john': {}, 'kitty': {'sound': 'meow', 'friends': ['doggy']}},
			{'doggy': {'sound': 'ruff'}, 'john': {}, 'kitty': {'sound': 'meow'}},
			{'doggy': {'sound': 'ruff'}, 'kitty': {'sound': 'meow'}},
			{'kitty': {'sound': 'meow'}},
			{}
		]

		self.assertTrue(len(action_strings.split())==len(actions)==len(states)-1)

		for i,s in enumerate(action_strings.split()):
			a = string_to_action_object(s,self.locals)
			self.assertEqual(a,actions[i])

			a.execute(self.locals['sim'])
			self.assertEqual(self.locals['sim'].get_contents(),states[i+1])

		rev_states = list(reversed(states))
		for i,a in enumerate(reversed(actions)):
			a.rollback(self.locals['sim'])
			self.assertEqual(self.locals['sim'].get_contents(),rev_states[i+1])



	def test_secondary_action_objects(self):
		john = Person('john')
		doggy = Animal('doggy',sound='ruff',owner=john)
		kitty = Animal('kitty',sound='meow',owner=john,friends=[doggy])
		sim = SimulationState([john,doggy,kitty])
		
		action = RemoveScalarAttr(doggy,'sound')
		expandsto = SetAttr.make(doggy,'sound',None)
		self.assertEqual(action.expand(),expandsto)

		action = RemoveEdgeAttr(doggy,'friends')
		expandsto = [RemoveEdge.make(doggy,'friends',kitty)]
		self.assertEqual(action.expand(),expandsto)

		action = RemoveEdgeAttr(doggy,'owner')
		expandsto = [RemoveEdge.make(doggy,'owner',john)]
		self.assertEqual(action.expand(),expandsto)

		action = RemoveAllEdges(doggy)
		expandsto = [RemoveEdgeAttr(doggy,'friends'), RemoveEdgeAttr(doggy,'owner')]
		self.assertEqual(action.expand(),expandsto)

		action = Remove(doggy)
		expandsto = [RemoveAllEdges(doggy),RemoveNode.make(doggy)]
		self.assertEqual(action.expand(),expandsto)