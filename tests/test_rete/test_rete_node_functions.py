from wc_rules.matcher.functionalize2 import *
from wc_rules.matcher.core import *
from wc_rules.schema.base import BaseClass
from wc_rules.graph.examples import *
from wc_rules.graph.canonical_labeling import canonical_label
import unittest

class X(BaseClass):
	pass
class Y(X):
	pass

def make_token(entry={},action=''):
	return {'entry':entry,'action':action}

class TestReteNodeFunctions(unittest.TestCase): 

	def test_start_node(self):
		# configuring Rete net methods
		net = ReteNet()
		net.add_node(type='start',core=BaseClass)
		net.add_behavior(StartNode(),'function_node_start')
		self.assertTrue('function_node_start' in net.list_behaviors())
		
		# building Rete net arch
		node = net.get_node(type='start')
		self.assertEqual(node.state.length_characteristics(), [0,0,None])
		
		# sending a token
		token = make_token()
		net.function_node_start(node,token)
		self.assertEqual(node.state.length_characteristics(), [0,1,None])
		self.assertTrue(token in node.state.outgoing)

	def test_class_node(self):
		net = ReteNet()
		net.add_node(type='class',core=X)
		net.add_behavior(ClassNode(),'function_node_class')
		self.assertTrue('function_node_class' in net.list_behaviors())
		
		node = net.get_node(core=X)
		self.assertEqual(node.state.length_characteristics(), [0,0,None])
		
		token = make_token()
		token['_class'] = Y
		net.function_node_class(node,token)
		self.assertEqual(node.state.length_characteristics(), [0,1,None])
		self.assertTrue(token in node.state.outgoing)

	def test_canonical_label_single_node(self):
		g,nsyms = single_node()
		mapping, clabel, group = canonical_label(g)
		net = ReteNet()
		net.add_node(type='canonical_label',core=clabel,symmetry_group=group)
		net.initialize_cache(clabel,clabel.names)
		net.add_behavior(CanonicalLabelNode(),'function_node_canonical_label')
		self.assertTrue('function_node_canonical_label' in net.list_behaviors())
		
		node = net.get_node(core=clabel)
		self.assertEqual(node.state.length_characteristics(), [0,0,0])
		
		token = make_token({'a':g['x']},'AddEntry')
		net.function_node_canonical_label(node,token)
		self.assertEqual(node.state.length_characteristics(), [0,1,1])
		self.assertTrue(len(net.filter_cache(clabel,{'a':g['x']})) > 0)

		node.state.flush_outgoing()
		token = make_token({'a':g['x']},'RemoveEntry')
		net.function_node_canonical_label(node,token)
		self.assertEqual(node.state.length_characteristics(), [0,1,0])
		self.assertTrue(len(net.filter_cache(clabel,{'a':g['x']})) == 0)
		
	def test_canonical_label_single_asymmetrical_edge(self):
		g,nsyms = single_edge_asymmetric()
		mapping, clabel, group = canonical_label(g)
		net = ReteNet()
		net.add_node(type='canonical_label',core=clabel,symmetry_group=group)
		net.initialize_cache(clabel,clabel.names)
		net.add_behavior(CanonicalLabelNode(),'function_node_canonical_label')
		self.assertTrue('function_node_canonical_label' in net.list_behaviors())
		
		node = net.get_node(core=clabel)
		self.assertEqual(node.state.length_characteristics(), [0,0,0])
		
		token = make_token({'a':g['x'],'b':g['y']},'AddEntry')
		net.function_node_canonical_label(node,token)
		self.assertEqual(node.state.length_characteristics(), [0,1,1])
		self.assertTrue(len(net.filter_cache(clabel,{'a':g['x']})) > 0)

		node.state.flush_outgoing()
		token = make_token({'a':g['x']},'RemoveEntry')
		net.function_node_canonical_label(node,token)
		self.assertEqual(node.state.length_characteristics(), [0,1,0])
		self.assertTrue(len(net.filter_cache(clabel,{'a':g['x']})) == 0)

	