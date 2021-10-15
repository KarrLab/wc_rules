from wc_rules.schema.entity import Entity
from wc_rules.schema.attributes import BooleanAttribute, ManyToOneAttribute
from wc_rules.schema.actions import AddNode,RemoveNode,AddEdge,RemoveEdge
from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.simulator.simulator import SimulationState
from wc_rules.matcher.core import default_rete_net
from wc_rules.graph.canonical_labeling import canonical_label
import math
import unittest

class X(Entity):
	pass

class Y(X):
	z = ManyToOneAttribute('Z',related_name='y')

class Z(X):
	pass


class TestRete(unittest.TestCase):

	def test_single_node_canonical_label(self):
		net = default_rete_net()
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
		self.assertEqual(gnode.state.cache[0]['a'].id,'x1')
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
		net = default_rete_net()
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
		net = default_rete_net()
		ss = SimulationState(matcher=net)
		
		g = GraphContainer(Y('y',z=Z('z')).get_connected())
		m,L,G = canonical_label(g)
		net.initialize_canonical_label(L,G)
		net.initialize_collector(L,'YZEdge')
		gnode, collector = net.get_node(core=L), net.get_node(core='collector_YZEdge')


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

	def test_two_edges_canonical_label(self):
		net = default_rete_net()
		ss = SimulationState(matcher=net)
		
		g = GraphContainer(Z('z',y=[Y('y1'),Y('y2')]).get_connected())
		m,L,G = canonical_label(g)
		net.initialize_canonical_label(L,G)
		net.initialize_collector(L,'ZYYGraph')
		gnode, collector = net.get_node(core=L), net.get_node(core='collector_ZYYGraph')

		# command to push nodes y1,y2,z1, and edge y1-z1
		ss.push_to_stack([
			AddNode.make(Y,'y1'),
			AddNode.make(Y,'y2'),
			AddNode.make(Z,'z1'),
			AddEdge('y1','z','z1','y'),
			]
		)
		ss.simulate()
		
		# both the rete node for the graph as well
		# as the downstream collector 
		# should have zero cache entries
		self.assertEqual(len(gnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),0)
		
		# add edge y2-z1
		ss.push_to_stack(AddEdge('y2','z','z1','y'))
		ss.simulate()

		# rete node for graph should have two entries
		# (z1-y1-y2) and (z2-y2-y1)
		# and collector should have two entries as well
		self.assertEqual(len(gnode.state.cache),2)
		self.assertEqual(len(collector.state.cache),2)
		
		# remove edge y1-z1
		ss.push_to_stack(RemoveEdge('y1','z','z1','y'))
		ss.simulate()

		# rete node for graph should have no entries
		# but collector should have four entries 
		# (two for add, two for remove)
		self.assertEqual(len(gnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),4)


	def test_n_edges_canonical_label(self):
		net = default_rete_net()
		ss = SimulationState(matcher=net)

		n=6
		z = Z('z1',y=[Y(f'y{i}') for i in range(1,1+n)])
		g = GraphContainer(z.get_connected())
		m,L,G = canonical_label(g)
		net.initialize_canonical_label(L,G)
		net.initialize_collector(L,'ZYnGraph')
		gnode, collector = net.get_node(core=L), net.get_node(core='collector_ZYnGraph')

		# command to push nodes z1, y1-y5
		ss.push_to_stack([AddNode.make(Z,'z1')] + [AddNode.make(Y,f'y{i}') for i in range(1,1+n)])
		ss.simulate()

		# add edges z1-[y1-yn-1] (n-1 edges)
		ss.push_to_stack([AddEdge(f'y{i}','z','z1','y') for i in range(1,n)])
		ss.simulate()

		# cache and collector should have zero entries
		self.assertEqual(len(gnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),0)

		ss.push_to_stack(AddEdge(f'y{n}','z','z1','y'))
		ss.simulate()

		# cache and collector should have n! add-entries
		self.assertEqual(len(gnode.state.cache),math.factorial(n))
		self.assertEqual(len(collector.state.cache),math.factorial(n))

		# remove z1-y1 edge
		ss.push_to_stack(RemoveEdge(f'y1','z','z1','y'))
		ss.simulate()
		
		#cache should be empty, but collector should have 2*n! entries
		self.assertEqual(len(gnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),2*math.factorial(n))


