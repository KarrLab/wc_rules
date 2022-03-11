from wc_rules.matcher.core import build_rete_net_class
from wc_rules.schema.chem import Molecule
from wc_rules.matcher.token import *
from wc_rules.graph.examples import get_canonical_label
import unittest

ReteNet = build_rete_net_class()

class TestNodeFunctions(unittest.TestCase):
	
	def test_function_node_start(self):
		token = make_node_token(Molecule,Molecule('mol1'),{})
		rn = ReteNet().initialize_start()
		node = rn.get_node(type='start')
		rn.function_node_start(node,token)
		self.assertTrue(token in node.state.outgoing)

	def test_function_node_canonical_label_single_node(self):
		rn = ReteNet().initialize_start()
		m, L, G = get_canonical_label('single_node')
		rn.initialize_canonical_label(L,G)

		_class = L.classes[0]
		node = rn.get_node(core=L)
		channel = rn.get_channel(target=L,type='transform')
		self.assertEqual(len(node.state.cache),0)
		self.assertEqual(len(node.state.outgoing),0)
		
		x1 = _class('x1')
		token = CacheToken(data={'a':x1},action='AddEntry',channel=channel.num)
		rn.function_node_canonical_label(node,token)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(node.state.outgoing),1)
		cached_record = node.state.cache.filter(token.data)[0]
		self.assertTrue(cached_record['a'] is x1)
		

		x2 = _class('x2')
		token = CacheToken(data={'a':x2},action='AddEntry',channel=channel.num)
		rn.function_node_canonical_label(node,token)
		self.assertEqual(len(node.state.cache),2)
		self.assertEqual(len(node.state.outgoing),2)
		cached_record = node.state.cache.filter(token.data)[0]
		self.assertTrue(cached_record['a'] is x2)
		
		token = CacheToken(data={'a':x1},action='RemoveEntry',channel=channel.num)
		rn.function_node_canonical_label(node,token)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(node.state.outgoing),3)
		self.assertEqual(len(node.state.cache.filter(dict(a=x1))),0)
		self.assertEqual(len(node.state.cache.filter(dict(a=x2))),1)


	def test_function_node_canonical_label_single_node(self):
		rn = ReteNet().initialize_start()
		m, L, G = get_canonical_label('single_edge_asymmetric')
		rn.initialize_canonical_label(L,G)

		C1,C2 = L.classes
		node = rn.get_node(core=L)
		channel = rn.get_channel(target=L,type='transform')
		self.assertEqual(len(node.state.cache),0)
		self.assertEqual(len(node.state.outgoing),0)

		x1,y1 = C1('x1'), C2('y1')
		x1.safely_add_edge('y',y1)
		token = CacheToken(data={'a':x1,'b':y1,'attr1':'y','attr2':'x'},action='AddEntry',channel=channel.num)
		rn.function_node_canonical_label(node,token)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(node.state.outgoing),1)
		cached_record = node.state.cache.filter({'a':x1})[0]
		self.assertEqual(cached_record['b'],y1)

		x2,y2 = C1('x2'), C2('y2')
		x2.safely_add_edge('y',y2)
		token = CacheToken(data={'a':x2,'b':y2,'attr1':'y','attr2':'x'},action='AddEntry',channel=channel.num)
		rn.function_node_canonical_label(node,token)
		self.assertEqual(len(node.state.cache),2)
		self.assertEqual(len(node.state.outgoing),2)
		cached_record = node.state.cache.filter({'a':x2})[0]
		self.assertEqual(cached_record['b'],y2)

		token = CacheToken(data={'a':x1,'b':y1,'attr1':'y','attr2':'x'},action='RemoveEntry',channel=channel.num)
		rn.function_node_canonical_label(node,token)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(node.state.outgoing),3)
		self.assertEqual(len(node.state.cache.filter(dict(a=x1))),0)
		self.assertEqual(len(node.state.cache.filter(dict(a=x2))),1)

		# nothing should happen since it is referring to wrong attrs
		token = CacheToken(data={'a':x1,'b':y1,'attr1':'p','attr2':'q'},action='RemoveEntry',channel=channel.num)
		rn.function_node_canonical_label(node,token)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(node.state.outgoing),3)
		self.assertEqual(len(node.state.cache.filter(dict(a=x1))),0)
		self.assertEqual(len(node.state.cache.filter(dict(a=x2))),1)

	def test_function_node_canonical_label_two_edges(self):
		rn = ReteNet().initialize_start()
		m, L, G = get_canonical_label('two_edges')
		rn.initialize_canonical_label(L,G)

		node1,node2 = sorted(rn.get_nodes(type='canonical_label'),key=lambda n: len(n.core.names))
		ch1, ch2 = sorted(rn.get_channels(type='transform',target=L),key=lambda ch: ch.num)
		self.assertEqual(node1.state.cache.fields,['a','b'])
		X,Y = node1.core.classes
		x1, y1, y2 = X('x1'), Y('y1'), Y('y2')

		node1.state.cache.insert({'a':x1,'b':y1})
		token = ch1.data.transformer.transform(CacheToken(data={'a':x1,'b':y1},action='AddEntry'),channel=ch1.num)
		self.assertEqual(token.data,{'a':x1,'b':y1})
		rn.function_node_canonical_label(node2,token)
		token = ch2.data.transformer.transform(CacheToken(data={'a':x1,'b':y1},action='AddEntry'),channel=ch2.num)
		self.assertEqual(token.data,{'a':x1,'c':y1})
		rn.function_node_canonical_label(node2,token)

		self.assertEqual(len(node1.state.cache),1)
		self.assertEqual(len(node2.state.cache),0)
		
		node1.state.cache.insert({'a':x1,'b':y2})
		token = ch1.data.transformer.transform(CacheToken(data={'a':x1,'b':y2},action='AddEntry'),channel=ch1.num)
		self.assertEqual(token.data,{'a':x1,'b':y2})
		rn.function_node_canonical_label(node2,token)
		token = ch2.data.transformer.transform(CacheToken(data={'a':x1,'b':y2},action='AddEntry'),channel=ch2.num)
		self.assertEqual(token.data,{'a':x1,'c':y2})
		rn.function_node_canonical_label(node2,token)

		self.assertEqual(len(node1.state.cache),2)
		self.assertEqual(len(node2.state.cache),2)
		self.assertEqual(len(node2.state.cache.filter({'a':x1,'b':y1,'c':y2})), 1)
		self.assertEqual(len(node2.state.cache.filter({'a':x1,'b':y2,'c':y1})), 1)
		

		x2, y3, y4 = X('x2'), Y('y3'), Y('y4')
		node1.state.cache.insert({'a':x2,'b':y3})
		token = ch1.data.transformer.transform(CacheToken(data={'a':x2,'b':y3},action='AddEntry'),channel=ch1.num)
		rn.function_node_canonical_label(node2,token)
		token = ch2.data.transformer.transform(CacheToken(data={'a':x2,'b':y3},action='AddEntry'),channel=ch2.num)
		rn.function_node_canonical_label(node2,token)

		self.assertEqual(len(node1.state.cache),3)
		self.assertEqual(len(node2.state.cache),2)
		
		node1.state.cache.insert({'a':x2,'b':y4})
		token = ch1.data.transformer.transform(CacheToken(data={'a':x2,'b':y4},action='AddEntry'),channel=ch1.num)
		rn.function_node_canonical_label(node2,token)
		token = ch2.data.transformer.transform(CacheToken(data={'a':x2,'b':y4},action='AddEntry'),channel=ch2.num)
		rn.function_node_canonical_label(node2,token)
		
		self.assertEqual(len(node1.state.cache),4)
		self.assertEqual(len(node2.state.cache),4)
		