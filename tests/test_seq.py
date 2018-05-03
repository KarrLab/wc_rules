"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-05
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import bioseq,utils
import unittest


class TestSeq(unittest.TestCase):

    def test_sequence_init(self):
        X = bioseq.DNA().init_sequence('ATCGR')
        self.assertEqual(X.sequence,'ATCGR')
        with self.assertRaises(utils.SeqError):
            X = bioseq.DNA().init_sequence('ATCGR',ambiguous=False)
        X = bioseq.DNA().init_sequence('ATCG',ambiguous=False)
        self.assertEqual(X.sequence,'ATCG')
        with self.assertRaises(utils.SeqError):
            X = bioseq.DNA().init_sequence('ZZZZ')

        X = bioseq.RNA().init_sequence('AUCGR')
        self.assertEqual(X.sequence,'AUCGR')
        with self.assertRaises(utils.SeqError):
            X = bioseq.RNA().init_sequence('AUCGR',ambiguous=False)
        X = bioseq.RNA().init_sequence('AUCG',ambiguous=False)
        self.assertEqual(X.sequence,'AUCG')
        with self.assertRaises(utils.SeqError):
            X = bioseq.RNA().init_sequence('ZZZZ')

        X = bioseq.Protein().init_sequence('ACDEFBXZ')
        self.assertEqual(X.sequence,'ACDEFBXZ')
        with self.assertRaises(utils.SeqError):
            X = bioseq.Protein().init_sequence('ACDEFBXZ',ambiguous=False)
        X = bioseq.Protein().init_sequence('ACDEF',ambiguous=False)
        self.assertEqual(X.sequence,'ACDEF')
        with self.assertRaises(utils.SeqError):
            X = bioseq.Protein().init_sequence('1234')

    def test_compatibility_between_sites_and_molecules(self):
        X = bioseq.DNA().init_sequence('ATCGAT')
        f = bioseq.PolynucleotideFeature().set_molecule(X)
        self.assertEqual(f.molecule,X)
        X = bioseq.RNA().init_sequence('AUCGAU')
        f.set_molecule(X)
        self.assertEqual(f.molecule,X)
        with self.assertRaises(utils.AddError):
            f = bioseq.PolypeptideFeature().set_molecule(X)

    def test_sequence_feature(self):
        inputstr = 'ATCGAT'
        X = bioseq.DNA().init_sequence(inputstr,ambiguous=False)
        f = bioseq.PolynucleotideFeature().set_molecule(X)

        self.assertEqual([f.position,f.length,f.get_sequence()],[0,0,''])

        f.set_position_and_length(0,1)
        self.assertEqual(f.get_sequence(),'A')

        f.set_position_and_length(5,1)
        self.assertEqual(f.get_sequence(),'T')

        f.set_position_and_length(0,6)
        self.assertEqual(f.get_sequence(),inputstr)

        f.set_position_and_length(6,0)
        self.assertEqual(f.get_sequence(),'')

        with self.assertRaises(utils.SeqError):
            f.set_position_and_length(-1,0)
        with self.assertRaises(utils.SeqError):
            f.set_position_and_length(0,-1)
        with self.assertRaises(utils.SeqError):
            f.set_position_and_length(6,1)
            f._verify_feature(f.molecule,f.position,f.length)

        # checking in absence of molecule
        f1 = bioseq.PolynucleotideFeature().set_position_and_length(0,1)
        self.assertEqual(f1.molecule,None)
        f1.set_position_and_length(6,1)
        with self.assertRaises(utils.SeqError):
            f1.set_position_and_length(-1,0)
        with self.assertRaises(utils.SeqError):
            f1.set_position_and_length(0,-1)
