from wc_rules.schema.base import BaseClass
from wc_rules.schema.attributes import *
from wc_rules.schema.actions import *
from wc_rules.simulator.simulator import SimulationState
from wc_rules.matcher.core import default_rete_net
import unittest


class Animal(BaseClass):
	sound = StringAttribute()
	friends = ManyToManyAttribute('Animal',related_name='friends')

class Person(BaseClass):
	pets = OneToManyAttribute(Animal,related_name='owner')

class ReportCard(BaseClass):
	comment = StringAttribute()
	passfail = BooleanAttribute()
	bio = IntegerAttribute()
	math = FloatAttribute()
	owner = OneToOneAttribute(Person,related_name='card')
	signatories = ManyToManyAttribute(Person,related_name='cards')

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
			RemoveEdge = RemoveEdge,
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
		
		action = RemoveLiteralAttr(doggy,'sound')
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

	
	def test_attached_methods(self):
		# comment = StringAttribute()
		# passfail = BooleanAttribute()
		# math = IntegerAttribute()
		# bio = FloatAttribute()
		# owner = OneToOneAttribute(Person,related_name='card')
		# signatories = ManyToManyAttribute(Person,related_name='cards')
		
		john = Person('john')
		jim = Person('jim')
		jack = Person('jack')
		jill = Person('jill')
		card = ReportCard('card',comment='Bad!',passfail=False,math=0,bio=0.1,owner=john,signatories=[jack])
		methodnames = '''
		set_comment
		remove_comment
		set_passfail
		setTrue_passfail
		setFalse_passfail
		flip_passfail
		remove_passfail
		set_bio
		increment_bio
		decrement_bio
		remove_bio
		set_math
		increment_math
		decrement_math
		add_owner
		remove_owner
		add_signatories
		remove_signatories
		'''.split()

		self.assertTrue(all([hasattr(card,x) for x in methodnames]))

		self.assertEqual( card.set_comment("Good!"), SetAttr('card','comment','Good!','Bad!') )
		self.assertEqual( card.remove_comment(), SetAttr('card','comment',None,'Bad!') )
		self.assertEqual( card.set_passfail(True), SetAttr('card','passfail',True,False) )
		self.assertEqual( card.setTrue_passfail(), SetTrue(card,'passfail') )
		self.assertEqual( card.setFalse_passfail(), SetFalse(card,'passfail') )
		self.assertEqual( card.remove_passfail(), SetAttr('card','passfail',None,False))
		self.assertEqual( card.flip_passfail(), Flip(card,'passfail') )
		self.assertEqual( card.set_bio(96.2), SetAttr('card','bio',96.2,0.1))
		self.assertEqual( card.increment_bio(93.1), Increment(card,'bio',93.1))
		self.assertEqual( card.decrement_bio(93.1), Decrement(card,'bio',93.1))
		self.assertEqual( card.remove_bio(), SetAttr('card','bio',None,0.1))
		self.assertEqual( card.set_math(96), SetAttr('card','math',96,0))
		self.assertEqual( card.increment_math(93), Increment(card,'math',93))
		self.assertEqual( card.decrement_math(93), Decrement(card,'math',93))
		self.assertEqual( card.remove_math(), SetAttr('card','math',None,0))
		self.assertEqual( card.add_owner(john), [AddEdge('card','owner','john','card')])
		self.assertEqual( card.remove_owner(john), [RemoveEdge('card','owner','john','card')])
		self.assertEqual( card.remove_owner(), RemoveEdgeAttr(card,'owner'))
		self.assertEqual( card.add_signatories(jack,jill), [AddEdge('card','signatories','jack','cards'), AddEdge('card','signatories','jill','cards')] )
		self.assertEqual( card.remove_signatories(jack,jill), [RemoveEdge('card','signatories','jack','cards'), RemoveEdge('card','signatories','jill','cards')] )
		self.assertEqual( card.remove_signatories(), RemoveEdgeAttr(card,'signatories'))
		self.assertEqual( card.remove_all_edges(), RemoveAllEdges(card))
		self.assertEqual( card.remove(), Remove(card))


	def test_expand_behavior(self):
		john = Person('john')
		jim = Person('jim')
		jack = Person('jack')
		jill = Person('jill')
		attrs = {'comment':'Bad!', 'passfail':False,'math':0, 'bio':0.1}
		attrs2 = {'owner':john, 'signatories':[jack]}
		card = ReportCard('card',**attrs,**attrs2)
		
		self.assertEqual( SetTrue(card,'passfail').expand(), SetAttr('card','passfail',True,False) )
		self.assertEqual( SetFalse(card,'passfail').expand(), SetAttr('card','passfail',False,False) )
		self.assertEqual( Flip(card,'passfail').expand(), SetAttr('card','passfail',True,False) )
		self.assertEqual( Increment(card,'bio',93.1).expand(), SetAttr('card','bio',93.1 + 0.1,0.1))
		self.assertEqual( Decrement(card,'bio',93.1).expand(), SetAttr('card','bio',0.1-93.1,0.1))
		self.assertEqual( Increment(card,'math',93).expand(), SetAttr('card','math',93,0))
		self.assertEqual( Decrement(card,'math',93).expand(), SetAttr('card','math',-93,0))
		self.assertEqual( RemoveEdgeAttr(card,'owner').expand(), [RemoveEdge('card','owner','john','card')])
		self.assertEqual( RemoveEdgeAttr(card,'signatories').expand(), [RemoveEdge('card','signatories','jack','cards') ])
		self.assertEqual( RemoveAllEdges(card).expand(), [RemoveEdgeAttr(card,'owner'), RemoveEdgeAttr(card,'signatories') ])
		self.assertEqual( Remove(card).expand(), [RemoveAllEdges(card), RemoveNode(ReportCard,'card',attrs)])


	def test_rete_simple(self):
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

		ss = default_rete_net()
		net = default_rete_net()
		net.initialize_class(Animal)
		net.initialize_class(Person)
		net.initialize_collector(Animal,'Animal')
		net.initialize_collector(Person,'Person')

		ss = SimulationState(matcher=net)
		ss.push_to_stack(actions)
		ss.simulate()

		collector_Animal = ss.matcher.get_node(core='collector_Animal')
		collector_Person = ss.matcher.get_node(core='collector_Person')
		
		# 2 AddNodes, 2 RemoveNodes, 1 SetAttr
		# 2x1 AddEdge + 2x1 RemoveEdge with John
		# 1x2 AddEdge + 1x2 RemoveEdge with each other
		self.assertEqual(len(collector_Animal.state.cache),13)
		
		# 1 AddNode, 1 RemoveNode
		# 1 AddEdge + 1 RemoveEdge with kitty
		# 1 AddEdge + 1 RemoveEdge with doggy
		self.assertEqual(len(collector_Person.state.cache),6)