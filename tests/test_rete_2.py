from wc_rules.schema.entity import Entity
from wc_rules.schema.attributes import *
from wc_rules.schema.actions import AddNode,RemoveNode,AddEdge,RemoveEdge, SetAttr
from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.modeling.rule import InstanceRateRule as Rule
from wc_rules.simulator.simulator import SimulationState
from wc_rules.matcher.core import ReteNet
from wc_rules.graph.canonical_labeling import canonical_label
from wc_rules.graph.collections import CanonicalForm
import math
import unittest

class X(Entity):
	a = BooleanAttribute()

	@computation
	def somefn(a):
		return str(a)
	

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


	def test_pattern_with_attr_updates(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)

		z = Z('z',y=[Y('y',a=True)])
		p = Pattern(parent=GraphContainer(z.get_connected()))

		net.initialize_pattern(p)
		net.initialize_collector(p,'p')
		pnode, collector = [net.get_node(core=x) for x in [p,'collector_p']]

		# First push three nodes Z, Y1(true), Y2(tree)
		# pattern and collector should be empty
		ss.push_to_stack([
			AddNode.make(Z,'z1'),
			AddNode.make(Y,'y1',{'a':True}),
			AddNode.make(Y,'y2',{'a':True})
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),0)

		# Now add edges Z-Y1, Z-Y2
		# pattern and collector should have two entries
		ss.push_to_stack([
			AddEdge('z1','y','y1','z'),
			AddEdge('z1','y','y2','z')
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),2)
		self.assertEqual(len(collector.state.cache),2)

		# Set Y2(true) to false
		# pattern should have 1, collector should have 3
		ss.push_to_stack([SetAttr('y2','a',False,True)])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),1)
		self.assertEqual(len(collector.state.cache),3)

		# Remove edge Z-Y1
		# pattern should have 0, collector should have 4
		ss.push_to_stack([
			RemoveEdge('y1','z','z1','y'),
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),4)

		# Add them back in
		# pattern should have 2, collector should have 6
		ss.push_to_stack([
			SetAttr('y2','a',True,False),
			AddEdge('y1','z','z1','y'),
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),2)
		self.assertEqual(len(collector.state.cache),6)

	def test_pattern_with_attr_updates_computefn(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)

		z = Z('z',y=[Y('y')])
		p = Pattern(
			parent=GraphContainer(z.get_connected()),
			constraints = ['y.somefn() == "True"']
			)

		net.initialize_pattern(p)
		net.initialize_collector(p,'p')
		pnode, collector = [net.get_node(core=x) for x in [p,'collector_p']]

		# First push three nodes Z, Y1(true), Y2(tree)
		# pattern and collector should be empty
		ss.push_to_stack([
			AddNode.make(Z,'z1'),
			AddNode.make(Y,'y1',{'a':True}),
			AddNode.make(Y,'y2',{'a':True})
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),0)

		# Now add edges Z-Y1, Z-Y2
		# pattern and collector should have two entries
		ss.push_to_stack([
			AddEdge('z1','y','y1','z'),
			AddEdge('z1','y','y2','z')
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),2)
		self.assertEqual(len(collector.state.cache),2)

		# Set Y2(true) to false
		# pattern should have 1, collector should have 3
		ss.push_to_stack([SetAttr('y2','a',False,True)])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),1)
		self.assertEqual(len(collector.state.cache),3)

		# Remove edge Z-Y1
		# pattern should have 0, collector should have 4
		ss.push_to_stack([
			RemoveEdge('y1','z','z1','y'),
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),0)
		self.assertEqual(len(collector.state.cache),4)

		# Add them back in
		# pattern should have 2, collector should have 6
		ss.push_to_stack([
			SetAttr('y2','a',True,False),
			AddEdge('y1','z','z1','y'),
			])
		ss.simulate()
		self.assertEqual(len(pnode.state.cache),2)
		self.assertEqual(len(collector.state.cache),6)


	def test_pattern_with_helper(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)

		p1 = Pattern(parent=GraphContainer([Y('n',a=True)]))
		z = Z('z',y=[Y('y')])
		p2 = Pattern(
			parent=GraphContainer(z.get_connected()),
			helpers = {'ypos':p1},
			constraints = ['ypos.contains(n=y) == True']
			)

		net.initialize_pattern(p2)
		# check retenet structure
		self.assertTrue(net.get_channel(source=p1,target=p2,type='update_pattern'))


		net.initialize_collector(p1,'p1')
		net.initialize_collector(p2,'p2')
		node1, node2, collector1, collector2 = [net.get_node(core=x) for x in [p1,p2,'collector_p1','collector_p2']]
		rete_nodes = [node1, collector1, node2, collector2]

		# First push two nodes Z, Y1(true), 
		# p1 must be non-empty, p2 must be empty
		ss.push_to_stack([
			AddNode.make(Z,'z1'),
			AddNode.make(Y,'y1',{'a':True}),
			])
		ss.simulate()

		for x,y in zip(rete_nodes,[1,1,0,0]):
			self.assertEqual(len(x.state.cache),y)

		# now add edge y1-z1
		# both p1 and p2 must be non-empty
		ss.push_to_stack([
			AddEdge('z1','y','y1','z'),
			])
		ss.simulate()

		for x,y in zip(rete_nodes,[1,1,1,1]):
			self.assertEqual(len(x.state.cache),y)

		# now set y1(false)
		# p1 and p2 must be empty, 
		# collectors must have 1 add and 1 remove entry each 
		ss.push_to_stack([
			SetAttr('y1','a',False,True)
			])
		ss.simulate()

		for x,y in zip(rete_nodes,[0,2,0,2]):
			self.assertEqual(len(x.state.cache),y)

		# set y1(true) and p1 and p2 must go back to 1 each
		# collectors increment by 1
		ss.push_to_stack([
			SetAttr('y1','a',True,False)
			])
		ss.simulate()

		for x,y in zip(rete_nodes,[1,3,1,3]):
			self.assertEqual(len(x.state.cache),y)

		# remove edge and p2 must go back to zero
		# collector_p2 increment by 1
		ss.push_to_stack([
			RemoveEdge('y1','z','z1','y'),
			])
		ss.simulate()

		for x,y in zip(rete_nodes,[1,3,0,4]):
			self.assertEqual(len(x.state.cache),y)


	def test_rule(self):
		net = ReteNet.default_initialization()
		ss = SimulationState(matcher=net)

		p1 = Pattern(GraphContainer([Y('y')]), constraints=['len(y.z)==0'])
		p2 = Pattern(GraphContainer([Z('z')]), constraints=['len(z.y) < max_y'], parameters=['max_y'])

		yz_rule = Rule(
			name = 'yz_rule',
			reactants = {'rY':p1,'rZ':p2},
			parameters = ['k','max_y'],
			rate_prefix = 'k',
			actions = ['rY.y.add_z(rZ.z)']
			)

		net.initialize_rule(name='yz_rule',parameters = {'k':1,'max_y':3},rule=yz_rule)
		net.initialize_collector('yz_rule','yz_rule')

		# push 4 Ys
		ss.push_to_stack([AddNode(Y,f'y{i}',{}) for i in range(1,5)])
		ss.simulate()

		# counts p1=4,p2=0, propensity=0, rule collector = 1 
		self.assertEqual(net.get_node(core=p1).state.count(),4)
		self.assertEqual(net.get_node(core=p2).state.count(),0)
		self.assertEqual(net.get_node(core='yz_rule').state.cache,0)
		self.assertEqual(len(net.get_node(core='collector_yz_rule').state.cache),1)

		# push 1 Z
		ss.push_to_stack([AddNode(Z,'z1',{})])
		ss.simulate()
		# counts p1=4,p2=1, propensity=4, rule collector = 2 
		self.assertEqual(net.get_node(core=p1).state.count(),4)
		self.assertEqual(net.get_node(core=p2).state.count(),1)
		self.assertEqual(net.get_node(core='yz_rule').state.cache,4)
		self.assertEqual(len(net.get_node(core='collector_yz_rule').state.cache),2)
		

		# Add edges from z1 to y1, y2, y3. Propensity should drop from 4 to 3 to 2 to 0
		ss.push_to_stack([AddEdge(f'y{i}','z','z1','y') for i in range(1,4)])
		ss.simulate()

		# counts p1=1,p2=0, propensity =0, collector=5
		self.assertEqual(net.get_node(core=p1).state.count(),1)
		self.assertEqual(net.get_node(core=p2).state.count(),0)
		self.assertEqual(net.get_node(core='yz_rule').state.cache,0)
		self.assertEqual(len(net.get_node(core='collector_yz_rule')),5)