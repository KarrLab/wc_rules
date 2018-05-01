"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-05
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import bio,seq,utils
from Bio.SeqFeature import FeatureLocation
import unittest


class TestSeq(unittest.TestCase):

    def test_sequence_init(self):
        X = bio.DNASequenceMolecule().init_sequence('ATCGR')
        self.assertEqual(X.sequence,'ATCGR')
        with self.assertRaises(utils.SeqError):
            X = bio.DNASequenceMolecule().init_sequence('ATCGR',ambiguous=False)
        X = bio.DNASequenceMolecule().init_sequence('ATCG',ambiguous=False)
        self.assertEqual(X.sequence,'ATCG')
        with self.assertRaises(utils.SeqError):
            X = bio.DNASequenceMolecule().init_sequence('ZZZZ')

        X = bio.RNASequenceMolecule().init_sequence('AUCGR')
        self.assertEqual(X.sequence,'AUCGR')
        with self.assertRaises(utils.SeqError):
            X = bio.RNASequenceMolecule().init_sequence('AUCGR',ambiguous=False)
        X = bio.RNASequenceMolecule().init_sequence('AUCG',ambiguous=False)
        self.assertEqual(X.sequence,'AUCG')
        with self.assertRaises(utils.SeqError):
            X = bio.RNASequenceMolecule().init_sequence('ZZZZ')

        X = bio.ProteinSequenceMolecule().init_sequence('ACDEFBXZ')
        self.assertEqual(X.sequence,'ACDEFBXZ')
        with self.assertRaises(utils.SeqError):
            X = bio.ProteinSequenceMolecule().init_sequence('ACDEFBXZ',ambiguous=False)
        X = bio.ProteinSequenceMolecule().init_sequence('ACDEF',ambiguous=False)
        self.assertEqual(X.sequence,'ACDEF')
        with self.assertRaises(utils.SeqError):
            X = bio.ProteinSequenceMolecule().init_sequence('1234')

    def test_sequence_feature(self):
        inputstr = 'ATCGAT'
        X = bio.DNASequenceMolecule().init_sequence(inputstr,ambiguous=False)
        f = seq.SequenceFeature().set_molecule(X)

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

        # checking in absence of molecule
        f1 = seq.SequenceFeature().set_position_and_length(0,1)
        self.assertEqual(f1.molecule,None)
        f1.set_position_and_length(6,1)
        with self.assertRaises(utils.SeqError):
            f1.set_position_and_length(-1,0)
        with self.assertRaises(utils.SeqError):
            f1.set_position_and_length(0,-1)
