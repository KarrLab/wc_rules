from wc_rules.schema.seq import SequenceMolecule, SequenceFeature
from wc_rules.modeling.seqpattern import SequenceFeaturePattern, OverlappingFeaturesPattern
from wc_rules.matcher.core import build_rete_net_class
from wc_rules.matcher.token import *

import unittest

class SeqMol(SequenceMolecule):
	pass

class SeqFeat(SequenceFeature):
	pass

class Seq1(SequenceMolecule):
	pass

class Feat1(SequenceFeature):
	pass

class Feat2(SequenceFeature):
	pass


class TestSeqPattern(unittest.TestCase):


	def test_sequence_feature_pattern(self):
		ReteNet = build_rete_net_class()

		p = SequenceFeaturePattern(M=SeqMol,S=SeqFeat)
		net = ReteNet()
		net.initialize_start()
		net.initialize_pattern(p)
		ppcache = net.get_node(core=p).state.cache

		# note that this is simultaneously testing @cache_methods
		# and add_cache_methods
		self.assertTrue(hasattr(ppcache,'overlaps'))

		m1 = SeqMol('m1',sequence='ATCGATCG')
		s1 = SeqFeat('s1',start=1,end=4)
		m1.sites.add(s1)
		tokens = [ 
			make_node_token(SeqMol,m1,'AddNode'),
			make_node_token(SeqFeat,s1,'AddNode'), 
			make_edge_token(SeqMol,m1,'sites',SeqFeat,s1,'molecule','AddEdge'),
			make_edge_token(SeqFeat,s1,'molecule',SeqMol,m1,'sites','AddEdge')
			]
		net.process_tokens(tokens)	
		self.assertEqual(ppcache.overlaps(molecule=m1,start=0),False)
		self.assertEqual(ppcache.overlaps(molecule=m1,start=0,end=2),True)
		self.assertEqual(ppcache.overlaps(molecule=m1,start=4,end=5),False)
		self.assertEqual(ppcache.overlaps(molecule=m1,start=3,end=5),True)

	def test_overlapping_features_pattern(self):
		ReteNet = build_rete_net_class()
		p = OverlappingFeaturesPattern(
			molecule = Seq1('seq1'),
			site1 = Feat1('feat1'),
			site2 = Feat2('feat2')
		)
		net = ReteNet()
		net.initialize_start()
		net.initialize_pattern(p)
		ppcache = net.get_node(core=p).state.cache
		self.assertEqual(len(ppcache),0)

		m1 = Seq1('m1',sequence='ATCGATCGATCG')
		s1 = Feat1('s1',start=1,end=4)
		s2 = Feat2('s2',start=4,end=7)
		m1.sites = [s1,s2]
		tokens = [ 
			make_node_token(Seq1,m1,'AddNode'),
			make_node_token(Feat1,s1,'AddNode'), 
			make_node_token(Feat2,s2,'AddNode'), 
			make_edge_token(Seq1,m1,'sites',Feat1,s1,'molecule','AddEdge'),
			make_edge_token(Feat1,s1,'molecule',Seq1,m1,'sites','AddEdge'),
			make_edge_token(Seq1,m1,'sites',Feat2,s2,'molecule','AddEdge'),
			make_edge_token(Feat2,s2,'molecule',Seq1,m1,'sites','AddEdge')
			]
		net.process_tokens(tokens)	
		self.assertEqual(len(ppcache),0)

		s1.end = 5
		tokens = [make_attr_token(Feat1,s1,'end','SetAttr')]
		net.process_tokens(tokens)	
		self.assertEqual(len(ppcache),1)
		self.assertEqual(ppcache.filter()[0],{'seq1':m1,'feat1':s1,'feat2':s2})
		
		s2.start = 5
		tokens = [make_attr_token(Feat2,s2,'start','SetAttr')]
		net.process_tokens(tokens)	
		self.assertEqual(len(ppcache),0)

		s1.end = 10
		tokens = [make_attr_token(Feat1,s1,'end','SetAttr')]
		net.process_tokens(tokens)	
		self.assertEqual(len(ppcache),1)
		self.assertEqual(ppcache.filter()[0],{'seq1':m1,'feat1':s1,'feat2':s2})
		
