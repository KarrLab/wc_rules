from wc_rules.matcher.core import build_rete_net_class
from wc_rules.schema.chem import Molecule
from wc_rules.matcher.token import *
from wc_rules.graph.examples import get_canonical_label
import unittest

ReteNet = build_rete_net_class()

class TestChannelFunctions(unittest.TestCase):
	
	def test_function_channel_pass(self):
		
		rn = ReteNet().initialize_start().initialize_receiver(type='start')
		start,receiver = rn.get_node(type='start'), rn.get_node(type='receiver')
		channel = rn.get_channel(type='pass')
		token = {'foo':'baz'}
		rn.function_channel_pass(channel,token)
		self.assertTrue(token in receiver.state.incoming)

	
	def test_function_channel_transform(self):
		rn = ReteNet().initialize_start()
		m,L,G = get_canonical_label('single_node')
		rn.initialize_canonical_label(L,G)
		node = rn.get_node(core=L)
		channel = rn.get_channel(type='transform')
		
		tr = channel.data.transformer
		self.assertEqual(channel.data.allowed_token_actions,set(['AddNode','RemoveNode']))
		self.assertEqual(tr.datamap,{'ref':'a'})
		
		# AddNode token -> AddEntry
		x1 = L.classes[0]('x1')
		token = make_node_token(L.classes[0],x1,'AddNode')
		self.assertEqual(token.data,{'ref':x1})
		rn.function_channel_transform(channel,token)
		self.assertEqual(len(node.state.incoming),1)
		cached_token = node.state.incoming.pop()
		self.assertEqual(cached_token.data,{'a':x1})
		self.assertEqual(cached_token.action,'AddEntry')

		# RemoveNode token -> RemoveEntry
		token = make_node_token(L.classes[0],x1,'RemoveNode')
		rn.function_channel_transform(channel,token)
		self.assertEqual(len(node.state.incoming),1)
		cached_token = node.state.incoming.pop()
		self.assertEqual(cached_token.data,{'a':x1})
		self.assertEqual(cached_token.action,'RemoveEntry')

		# key error when token.data is weird
		token = BasicToken(L.classes[0],'AddNode',{'some_key':x1})
		with self.assertRaises(KeyError):
			rn.function_channel_transform(channel,token)

		# no need to check if token.action is weird.
		# it wont be passed to the channel in the first place
		



