from wc_rules.schema.entity import Entity
from wc_rules.schema.chem import Molecule, Site
from wc_rules.matcher.core import build_rete_net_class
from wc_rules.matcher.token import *
from wc_rules.graph.examples import get_canonical_label
import unittest

ReteNet = build_rete_net_class()

class TestInitialize(unittest.TestCase):

	def test_class(self):
		rn = ReteNet()
		rn.initialize_start()
		rn.initialize_class(Molecule)
		rn.initialize_receiver(core=Entity)
		rn.initialize_receiver(core=Molecule)

		start = rn.get_node(type='start')
		rEnt, rMol = rn.get_nodes(type='receiver')
		self.assertEqual(len(rn.nodes.filter()),5)

		token = make_node_token(Molecule,Molecule('mol1'),{})
		start.state.incoming.append(token)
		rn.sync(start)

		# Molecule token must percolate to both receivers
		self.assertEqual(len(rEnt.state.cache),1)
		self.assertEqual(len(rMol.state.cache),1)

		token = make_node_token(Site,Site('site1'),{})
		start.state.incoming.append(token)
		rn.sync(start)

		# Site token must percolate only to entity-receiver
		self.assertEqual(len(rEnt.state.cache),2)
		self.assertEqual(len(rMol.state.cache),1)

	def test_canonical_label_single_node(self):
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')

		m,L,G = get_canonical_label('single_node')
		rn.initialize_canonical_label(L,G)
		rn.initialize_receiver(core=L)
		node = rn.get_node(core=L)
		receiver = rn.get_node(type='receiver')
		_class = L.classes[0]

		self.assertEqual(len(node.state.cache),0)
		self.assertEqual(len(receiver.state.cache),0)
		
		x1 = _class('x1')
		token = make_node_token(_class,x1,'AddNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(receiver.state.cache),1)
		
		x2 = _class('x2')
		token = make_node_token(_class,x2,'AddNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),2)
		self.assertEqual(len(receiver.state.cache),2)
		
		token = make_node_token(_class,x1,'RemoveNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(receiver.state.cache),3)

		token = make_node_token(_class,x2,'RemoveNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),0)
		self.assertEqual(len(receiver.state.cache),4)
		