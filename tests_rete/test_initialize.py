from wc_rules.schema.chem import Molecule
from wc_rules.schema.base import BaseClass
from wc_rules.schema.entity import Entity
from wc_rules.matcher.core import build_rete_net_class
import unittest

ReteNet = build_rete_net_class()

class TestInitialize(unittest.TestCase):

	def test_start(self):
		rn = ReteNet()
		rn.initialize_start()

		self.assertEqual(len(rn.nodes.filter()),1)
		self.assertEqual(len(rn.channels.filter()),0)

		node = rn.get_node(core=BaseClass)
		self.assertTrue(node.core==BaseClass)
		self.assertTrue(node.type=='start')

	def test_class(self):
		rn = ReteNet()
		rn.initialize_start()
		rn.initialize_class(Molecule)

		self.assertEqual(len(rn.nodes.filter()),3)
		self.assertEqual(len(rn.channels.filter()),2)

		node = rn.get_node(core=Molecule)
		self.assertTrue(node.core==Molecule)
		self.assertTrue(node.type=='class')

		channel = rn.get_channel(source=BaseClass,target=Entity)
		self.assertTrue(channel is not None)
		self.assertTrue(channel.type=='pass')
		
		channel = rn.get_channel(source=Entity,target=Molecule)
		self.assertTrue(channel is not None)
		self.assertTrue(channel.type=='pass')
		