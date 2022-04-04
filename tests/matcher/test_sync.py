from wc_rules.schema.base import BaseClass
from wc_rules.schema.entity import Entity
from wc_rules.matcher.core import build_rete_net_class
from wc_rules.matcher.token import make_node_token
import unittest


ReteNet = build_rete_net_class()

class TestSync(unittest.TestCase):

	def test_sync(self):
		rn = ReteNet()
		# assumes initialize_{x} and function_{x} for x \in {start,class,receiver}
		# assumes function_channel_pass

		self.assertTrue(hasattr(rn,'initialize_start'))
		self.assertTrue(hasattr(rn,'initialize_class'))
		self.assertTrue(hasattr(rn,'initialize_receiver'))
		self.assertTrue(hasattr(rn,'function_node_start'))
		self.assertTrue(hasattr(rn,'function_node_class'))
		self.assertTrue(hasattr(rn,'function_node_receiver'))
		self.assertTrue(hasattr(rn,'function_channel_pass'))
		
		rn.initialize_start()
		rn.initialize_class(Entity)
		rn.initialize_receiver(core=Entity)

		start, receiver = [rn.get_node(type=x) for x  in ['start','receiver']]
		# there must be 3 nodes: start (BaseClass), Entity, receiver
		# there must be 2 pass channels: start->Entity, Entity->receiver
		self.assertEqual(len(rn.nodes.filter()),3)
		self.assertEqual(len(rn.channels.filter()),2)

		token = make_node_token(Entity,Entity('ent01'),'AddNode')
		start.state.incoming.append(token)
		self.assertEqual(start.state.length_characteristics(),[1,0,None])
		self.assertEqual(receiver.state.length_characteristics(),[0,0,0])
		
		# For sync to work correctly on token:
		# # start node must discriminate _class==BaseClass
		# # then pass it through channel to Entity
		# # Entity node must discriminaate _class==Entity
		# # then pass it through channel to Receiver
		# # Receiver node must then append it to its own cache

		rn.sync(start)
		self.assertEqual(start.state.length_characteristics(),[0,0,None])
		self.assertEqual(receiver.state.length_characteristics(),[0,0,1])
		cached_token = receiver.state.cache[0]
		self.assertEqual(cached_token,token)


		