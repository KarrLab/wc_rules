from wc_rules.schema.entity import Entity
from wc_rules.schema.attributes import BooleanAttribute, ManyToOneAttribute
from wc_rules.schema.actions import AddNode,RemoveNode,AddEdge,RemoveEdge
from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.simulator.simulator import SimulationState
from wc_rules.matcher.core import ReteNet
from wc_rules.graph.canonical_labeling import canonical_label
from wc_rules.graph.collections import CanonicalForm
import math
import unittest

class X(Entity):
	pass

class Y(X):
	z = ManyToOneAttribute('Z',related_name='y')

class Z(X):
	pass


class TestRete(unittest.TestCase):

	def test_pattern_alias(self):
		# an alias pattern has a source, a mapping and no constraints
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)

		n=4
		z = Z('z1',y=[Y(f'y{i}') for i in range(1,1+n)])
		p = Pattern(parent=GraphContainer(z.get_connected()))

		net.initialize_pattern(p)
		# initialize must correctly identify it is an alias pattern
		self.assertEqual(net.get_node(core=p).data.get('alias',False),True)

		ch = net.get_channel(target=p,type='alias')
		g,mapping = ch.source, ch.data.mapping
		# this must be a canonical label
		self.assertEqual(isinstance(g,CanonicalForm),True)
		self.assertEqual(set(mapping.sources), set(g.names))
		self.assertEqual(set(mapping.targets), set(p.variables))

		pnode,gnode = [net.get_node(core=x) for x in [p,g]]
		net.initialize_collector(p,'p')
		net.initialize_collector(g,'g')
		pcollector, gcollector = [net.get_node(core=f'collector_{x}') for x in 'pg']

		# # command to push nodes z1, y1-yn
		ss.push_to_stack([AddNode.make(Z,'z1')] + [AddNode.make(Y,f'y{i}') for i in range(1,1+n)])
		ss.simulate()

		# # add edges z1-[y1-yn-1] (n-1 edges)
		ss.push_to_stack([AddEdge(f'y{i}','z','z1','y') for i in range(1,n)])
		ss.simulate()

		# # cache and collector should have zero entries
		# # pnode must not have a cache initialized
		self.assertTrue(pnode.state.cache is None)
		# # gnode, pcollector, gcollector should all have zero entries
		for x in [gnode,pcollector,gcollector]:
			self.assertEqual(len(x.state.cache),0)

		# # pushing n'th edge
		ss.push_to_stack([AddEdge(f'y{n}','z','z1','y')])
		ss.simulate()

		# # gnode, pcollector, gcollector should all have n! entries
		for x in [gnode,pcollector,gcollector]:
			self.assertEqual(len(x.state.cache),math.factorial(n))
		
		# check if filtering through alias works
		fil = net.filter_cache(p,{'z1':ss.resolve('z1')})
		self.assertEqual(len(fil),math.factorial(n))
		
		# # # remove z1-y1 edge
		ss.push_to_stack(RemoveEdge('y1','z','z1','y'))
		ss.simulate()
		
		# # # gnode should have zero entries 
		self.assertEqual(len(gnode.state.cache),0)
		# p and g collectors should have 2*n! entries
		for x in [pcollector,gcollector]:
			self.assertEqual(len(x.state.cache),2*math.factorial(n))
		
		# check if filtering through alias works
		fil = net.filter_cache(p,{'z1':'z1'})
		self.assertEqual(len(fil),0)
		
	def test_double_alias_pattern(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)

		n=3
		z = Z('z1',y=[Y(f'y{i}') for i in range(1,1+n)])
		p = Pattern(parent=GraphContainer(z.get_connected()))
		q = Pattern(parent=p)
		net.initialize_pattern(q)
		net.initialize_collector(q,'q')

		# # command to push nodes z1, y1-yn
		ss.push_to_stack([AddNode.make(Z,'z1')] + [AddNode.make(Y,f'y{i}') for i in range(1,1+n)])
		ss.simulate()
		ss.push_to_stack([AddEdge(f'y{i}','z','z1','y') for i in range(1,1+n)])
		ss.simulate()

		pnode, qnode = [net.get_node(core=x) for x in [p,q]]
		collector = net.get_node(core='collector_q')

		for x in [pnode,qnode]:
			self.assertEqual(x.data.get('alias',False),True)
			self.assertTrue(x.state.cache is None)


		self.assertEqual(len(collector.state.cache),math.factorial(n))
		self.assertEqual(len(net.filter_cache(q,{'z1':ss.resolve('z1')})), math.factorial(n))

