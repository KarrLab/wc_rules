from wc_rules.matcher.core import build_rete_net_class
from wc_rules.schema.chem import Molecule
from wc_rules.matcher.token import *
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

	


