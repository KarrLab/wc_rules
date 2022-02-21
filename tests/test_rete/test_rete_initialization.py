from wc_rules.matcher.initialize import *
from wc_rules.matcher.core import *
from wc_rules.schema.chem import Molecule
import unittest


class TestReteInitialization(unittest.TestCase): 
	def test_initialize_class(self):
		net = ReteNet()
		net.add_behavior(initialize_class,'initialize_class')
		net.add_behavior(initialize_start,'initialize_start')
		net.initialize_start()
		net.initialize_class(Molecule)
		self.assertEqual(len(net.nodes.filter()),3)
		self.assertEqual(len(net.channels.filter()),2)
		self.assertEqual(net.get_node(core=Molecule).core,Molecule)