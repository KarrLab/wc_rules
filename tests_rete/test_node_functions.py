from wc_rules.matcher.core import build_rete_net_class
from wc_rules.schema.chem import Molecule
from wc_rules.matcher.token import *
import unittest

ReteNet = build_rete_net_class()

class TestNodeFunctions(unittest.TestCase):
	
	def test_function_node_start(self):
		token = make_node_token(Molecule,Molecule('mol1'),{})
		rn = ReteNet().initialize_start()
		node = rn.get_node(type='start')
		rn.function_node_start(node,token)
		self.assertTrue(token in node.state.outgoing)


