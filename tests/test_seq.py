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

    
