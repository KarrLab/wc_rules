from wc_rules.schema.entity import Entity
from wc_rules.schema.chem import Molecule, Site
from wc_rules.matcher.core import build_rete_net_class
from wc_rules.matcher.token import *
from wc_rules.graph.examples import *
import random
import unittest

ReteNet = build_rete_net_class()

class TestEndToEnd(unittest.TestCase):

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

class TestEndToEndCanonicalLabel(unittest.TestCase):

	def test_single_node(self):
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


	def test_single_edge(self):
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')

		m,L,G = get_canonical_label('single_edge_asymmetric')
		rn.initialize_canonical_label(L,G)
		rn.initialize_receiver(core=L)
		node = rn.get_node(core=L)
		receiver = rn.get_node(type='receiver')
		C1,C2 = L.classes

		self.assertEqual(len(node.state.cache),0)
		self.assertEqual(len(receiver.state.cache),0)

		x1,y1 = C1('x1'), C2('y1')
		x1.safely_add_edge('y',y1)
		token = make_edge_token(C1,x1,'y',C2,y1,'x','AddEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(receiver.state.cache),1)
		
		x2,y2 = C1('x2'), C2('y2')
		x2.safely_add_edge('y',y2)
		token = make_edge_token(C1,x2,'y',C2,y2,'x','AddEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),2)
		self.assertEqual(len(receiver.state.cache),2)
		
		token = make_edge_token(C1,x1,'y',C2,y1,'x','RemoveEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),1)
		self.assertEqual(len(receiver.state.cache),3)
		
		token = make_edge_token(C1,x2,'y',C2,y2,'x','RemoveEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node.state.cache),0)
		self.assertEqual(len(receiver.state.cache),4)


	def test_two_edges(self):
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')

		m, L, G = get_canonical_label('two_edges')
		rn.initialize_canonical_label(L,G)

		node1,node2 = sorted(rn.get_nodes(type='canonical_label'),key=lambda n: len(n.core.names))
		self.assertEqual(node1.state.cache.fields,['a','b'])
		self.assertEqual(node2.state.cache.fields,['a','b','c'])
		X,Y = node1.core.classes
		x1, y1, y2 = X('x1'), Y('y1'), Y('y2')
		x2, y3, y4 = X('x1'), Y('y3'), Y('y4')
		
		x1.safely_add_edge('y',y1)
		token = make_edge_token(X,x1,'y',Y,y1,'x','AddEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),1)
		self.assertEqual(len(node2.state.cache),0)
		
		x1.safely_add_edge('y',y2)
		token = make_edge_token(X,x1,'y',Y,y2,'x','AddEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),2)
		self.assertEqual(len(node2.state.cache),2)
		
		x2.safely_add_edge('y',y3)
		token = make_edge_token(X,x2,'y',Y,y3,'x','AddEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),3)
		self.assertEqual(len(node2.state.cache),2)
		
		x2.safely_add_edge('y',y4)
		token = make_edge_token(X,x2,'y',Y,y4,'x','AddEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),4)
		self.assertEqual(len(node2.state.cache),4)

		# start removing edges
		x1.safely_remove_edge('y',y1)
		token = make_edge_token(X,x1,'y',Y,y1,'x','RemoveEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),3)
		self.assertEqual(len(node2.state.cache),2)
		
		x1.safely_remove_edge('y',y2)
		token = make_edge_token(X,x1,'y',Y,y2,'x','RemoveEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),2)
		self.assertEqual(len(node2.state.cache),2)
		
		x2.safely_remove_edge('y',y3)
		token = make_edge_token(X,x2,'y',Y,y3,'x','RemoveEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),1)
		self.assertEqual(len(node2.state.cache),0)
		
		x2.safely_remove_edge('y',y4)
		token = make_edge_token(X,x2,'y',Y,y4,'x','RemoveEdge')
		start.state.incoming.append(token)
		rn.sync(start)
		self.assertEqual(len(node1.state.cache),0)
		self.assertEqual(len(node2.state.cache),0)

	def test_spoke4(self):
		rn = ReteNet().initialize_start()
		start = rn.get_node(type='start')

		mapping,labeling,symmetry_group = get_canonical_label('spoke')
		rn.initialize_canonical_label(labeling,symmetry_group)

		nodes = rn.get_nodes(type='canonical_label')
		node1,node2 = nodes[0], nodes[-1]
		# node1 is a single edge
		# node2 is n-edges, where n is the number of spokes

		self.assertEqual(len(node1.core.names),2)
		self.assertEqual(len(node1.state.cache),0)
		self.assertEqual(len(node2.core.names),5)
		self.assertEqual(len(node2.state.cache),0)

		g,nsyms = spoke()

		for idx,n in g.iter_nodes():
			token = make_node_token(n.__class__,n,'AddNode')
			start.state.incoming.append(token)
			rn.sync(start)
		self.assertEqual(len(node1.state.cache),0)
		self.assertEqual(len(node2.state.cache),0)

		for e in g.iter_edges():
			n1,a1,n2,a2 = e.unpack()
			n1,n2 = [g[x] for x in [n1,n2]]
			c1,c2 = n1.__class__, n2.__class__
			tokens = [make_edge_token(*x) for x in [ (c1,n1,a1,c2,n2,a2,'AddEdge'), (c2,n2,a2,c1,n1,a1,'AddEdge') ] ]	
			for token in tokens:
				start.state.incoming.append(token)
				rn.sync(start)

		self.assertEqual(len(node1.state.cache),4)
		self.assertEqual(len(node2.state.cache),24)

		# removing even one edge should empty the cache for the spoke-graph
		# but the single-edge graph shd have three remaining matches
		e = random.sample(list(g.iter_edges()),1)[0]
		n1,a1,n2,a2 = e.unpack()
		n1,n2 = [g[x] for x in [n1,n2]]
		tokens = [make_edge_token(*x) for x in [ (c1,n1,a1,c2,n2,a2,'RemoveEdge'), (c2,n2,a2,c1,n1,a1,'RemoveEdge') ] ]	
		for token in tokens:
			start.state.incoming.append(token)
			rn.sync(start)

		self.assertEqual(len(node1.state.cache),3)
		self.assertEqual(len(node2.state.cache),0)



		



