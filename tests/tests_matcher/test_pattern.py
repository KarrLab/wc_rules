from wc_rules.modeling.pattern import Pattern, GraphContainer
from wc_rules.matcher.core import build_rete_net_class
from wc_rules.matcher.token import *
from wc_rules.graph.examples import X,Y

import unittest

ReteNet = build_rete_net_class()


class TestRetePatternInitialization(unittest.TestCase):
	# test the pattern, its incoming channel

	def test_pattern_alias(self):
		# an alias pattern is a pattern that is a pure graph
		# no expressions or attribute checks

		rn = ReteNet().initialize_start()
		px = Pattern(parent=GraphContainer([X('x')]))
		rn.initialize_pattern(px)
		rn_px = rn.get_node(core=px)
		channel = rn.get_channel(target=px)
		rn_parent = rn.get_node(core=channel.source)

		self.assertEqual(rn_px.core,px)
		self.assertEqual(rn_px.state.cache.target,rn_parent.state.cache)
		self.assertEqual(rn_px.state.cache.mapping,{'x':'a'})
		self.assertEqual(channel.data.transformer.datamap,{'a':'x'})
		actions = {'AddEntry':'AddEntry','RemoveEntry':'RemoveEntry'}
		self.assertEqual(channel.data.transformer.actionmap,actions)

	def test_pattern_double_alias(self):
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')
		
		px = Pattern(parent=GraphContainer([X('x')]))
		pxx = Pattern(parent=px)
		rn.initialize_pattern(pxx)

		rn_px, rn_pxx = [rn.get_node(core=x) for x in [px,pxx]]
		
		self.assertTrue(rn_px is not None)
		self.assertTrue(rn_pxx is not None)
		self.assertTrue(rn_pxx.state.cache.target is rn_px.state.cache.target)

	def test_pattern_edge_attribute(self):
		# no helpers
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')
		
		py = Pattern(
			parent=GraphContainer([Y('y')]),
			constraints=['len(y.x)==0']
		)
		rn.initialize_pattern(py)
		rn_py = rn.get_node(core=py)
		rn_parent = rn.get_node(type='canonical_label')
		self.assertTrue(rn_py is not None)
		self.assertTrue(rn_py.data.executables is not None)
		self.assertEqual(rn_py.data.executables.execs[0].code,'len(y.x) == 0')
		self.assertTrue(rn_py.data.caches is not None)
		self.assertEqual(rn_py.data.caches['parent'].target,rn_parent.state.cache)
		
		ch = rn.get_channel(source=Y,target=py,type='transform')
		self.assertTrue(ch is not None)
		self.assertEqual(ch.data.transformer.datamap,{'ref':'y','attr':'attr'})
		self.assertEqual(ch.data.transformer.actionmap,{'SetAttr':'VerifyEntry'})
		self.assertTrue(ch.data.filter_data({'attr':'x'}))
		self.assertTrue(ch.data.filter_data({'attr':'boo'}) == False)


class TestRetePatternBehavior(unittest.TestCase):
	# test insert/remove/filter

	def test_pattern_alias(self):
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')
		
		px = Pattern(parent=GraphContainer([X('x')]))
		rn.initialize_pattern(px)
		rn_px = rn.get_node(core=px)
		
		self.assertEqual(len(rn_px.state.cache.target),0)

		x1 = X('x1')
		token = make_node_token(X,x1,'AddNode')
		start.state.incoming.append(token)
		rn.sync(start)

		self.assertEqual(len(rn_px.state.cache.target),1)
		self.assertEqual(rn_px.state.cache.filter(),[{'x':x1}])
		self.assertEqual(rn_px.state.cache.filter({'x':x1}),[{'x':x1}])

		token = make_node_token(X,x1,'RemoveNode')
		start.state.incoming.append(token)
		rn.sync(start)

		self.assertEqual(len(rn_px.state.cache.target),0)
		
	def test_pattern_double_alias(self):

		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')
		
		px = Pattern(parent=GraphContainer([X('x')]))
		pxx = Pattern(parent=px)
		rn.initialize_pattern(pxx)

		rn_px, rn_pxx = [rn.get_node(core=x) for x in [px,pxx]]
		
		self.assertEqual(rn_pxx.state.cache.filter(),[])
		
		x1 = X('x1')
		token = make_node_token(X,x1,'AddNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(rn_pxx.state.cache.filter(),[{'x':x1}])
		
		token = make_node_token(X,x1,'RemoveNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(rn_pxx.state.cache.filter(),[])
		
	def test_pattern_edge_attribute(self):
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')
		
		py = Pattern(
			parent=GraphContainer([Y('y')]),
			constraints=['len(y.x)==0']
		)
		rn.initialize_pattern(py)
		rn_py = rn.get_node(core=py)
		self.assertEqual(rn_py.state.cache.filter(),[])
		
		x1,y1 = X('x1'), Y('y1')
		token = make_node_token(Y,y1,'AddNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(rn_py.state.cache.filter(),[{'y':y1}])

		y1.x = x1
		token = make_attr_token(Y,y1,'x','SetAttr')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(rn_py.state.cache.filter(),[])
		
		y1.x = None
		token = make_attr_token(Y,y1,'x','SetAttr')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(rn_py.state.cache.filter(),[{'y':y1}])
		
		token = make_node_token(Y,y1,'RemoveNode')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(rn_py.state.cache.filter(),[])
		

