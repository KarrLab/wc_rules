from wc_rules.schema.entity import Entity
from wc_rules.schema.attributes import BooleanAttribute, ManyToOneAttribute
from wc_rules.schema.actions import AddNode,RemoveNode,AddEdge,RemoveEdge
from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.simulator.simulator import SimulationState
from wc_rules.matcher.core import ReteNet
from wc_rules.graph.canonical_labeling import canonical_label

import unittest

class X(Entity):
	pass

class Y(X):
	z = ManyToOneAttribute('Z',related_name='y')

class Z(X):
	pass


class TestRete(unittest.TestCase):

	def test_single_node_canonical_label(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)
		
		m,L,G = canonical_label(GraphContainer([X('x')]))
		net.initialize_canonical_label(L,G)
		net.initialize_collector(L,'X')
		gnode,collector = net.get_node(core=L), net.get_node(core='collector_X')

		# Command to insert an instance X('x1')
		ss.push_to_stack(AddNode.make(X,'x1'))
		ss.simulate()

		# Rete nodes should have updated matches
		# gnode collects true matches X('')
		# collector collects all tokens coming out of gnode
		self.assertEqual(len(gnode.state.cache),1)
		self.assertEqual(gnode.state.cache[0]['a'],'x1')
		self.assertEqual(len(collector.state.cache),1)

		# Command to remove an instance X('x1')
		x1 = ss.resolve('x1')
		ss.push_to_stack(RemoveNode.make(x1))
		ss.simulate()

		# gnode cache shd be empty
		# but collector cache should have add-entry and delete-entry
		self.assertEqual(len(gnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),2)

	def test_single_node_branching_classes(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)
		
		gnodes = []
		for c,i in zip([X,Y,Z],['x','y','z']):
			m,L,G = canonical_label(GraphContainer([c(i)]))
			net.initialize_canonical_label(L,G)
			gnodes.append(net.get_node(core=L))
			
		
		# Adding three instances, one of X, one of Y, one of Z
		# since X<Y,Z, X shd have three matches, Y,Z one each
		for c,i in zip([X,Y,Z],['x','y','z']):
			ss.push_to_stack(AddNode.make(c,i+'1'))
		ss.simulate()

		cache_sizes = [len(g.state.cache) for g in gnodes]
		self.assertEqual(cache_sizes,[3,1,1])

		# Removing three instances, one of X, one of Y, one of Z
		for c,i in zip([X,Y,Z],['x','y','z']):
			ss.push_to_stack(RemoveNode.make(ss.resolve(i+'1')))
		ss.simulate()

		cache_sizes = [len(g.state.cache) for g in gnodes]
		self.assertEqual(cache_sizes,[0,0,0])
		
	def test_single_edge_canonical_label(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)
		
		g = GraphContainer(Y('y',z=Z('z')).get_connected())
		m,L,G = canonical_label(g)
		net.initialize_canonical_label(L,G)
		net.initialize_collector(L,'XYEdge')
		gnode, collector = net.get_node(core=L), net.get_node(core='collector_XYEdge')


		# command to push nodes y1 z1
		ss.push_to_stack([
			AddNode.make(Y,'y1'),
			AddNode.make(Z,'z1'),
			]
		)
		ss.simulate()

		# both the rete node for the edge as well
		# as the downstream collector 
		# should have zero cache entries
		self.assertEqual(len(gnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),0)
		
		# add edge y1-z1
		ss.push_to_stack(AddEdge('y1','z','z1','y'))
		ss.simulate()

		# rete node for edge and collector should have
		# one entry each
		self.assertEqual(len(gnode.state.cache),1)
		self.assertEqual(len(collector.state.cache),1)
		
		# remove edge y1-z1
		ss.push_to_stack(RemoveEdge('y1','z','z1','y'))
		ss.simulate()

		# rete node for edge should have no entries
		# but collector should have two entries 
		# (one for add, one for remove)
		self.assertEqual(len(gnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),2)
		



