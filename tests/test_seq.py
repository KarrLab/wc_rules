"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-05
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import bioseq,utils
import unittest


class TestSeq(unittest.TestCase):

    def test_sequence_init(self):
        X = bioseq.DNA().set_sequence('ATCGR')
        self.assertEqual(X.sequence,'ATCGR')
        with self.assertRaises(utils.SeqError):
            X = bioseq.DNA(use_permissive_alphabet=False).set_sequence('ATCGR')
            X.verify_sequence()
        X = bioseq.DNA(use_permissive_alphabet=False).set_sequence('ATCG')
        self.assertEqual(X.sequence,'ATCG')
        with self.assertRaises(utils.SeqError):
            X = bioseq.DNA().set_sequence('ZZZZ')
            X.verify_sequence()

        X = bioseq.RNA().set_sequence('AUCGR')
        self.assertEqual(X.sequence,'AUCGR')
        with self.assertRaises(utils.SeqError):
            X = bioseq.RNA(use_permissive_alphabet=False).set_sequence('AUCGR')
            X.verify_sequence()
        X = bioseq.RNA(use_permissive_alphabet=False).set_sequence('AUCG')
        self.assertEqual(X.sequence,'AUCG')
        with self.assertRaises(utils.SeqError):
            X = bioseq.RNA().set_sequence('ZZZZ')
            X.verify_sequence()

        X = bioseq.Protein().set_sequence('ACDEFBXZ')
        self.assertEqual(X.sequence,'ACDEFBXZ')
        with self.assertRaises(utils.SeqError):
            X = bioseq.Protein(use_permissive_alphabet=False).set_sequence('ACDEFBXZ')
            X.verify_sequence()
        X = bioseq.Protein(use_permissive_alphabet=False).set_sequence('ACDEF')
        self.assertEqual(X.sequence,'ACDEF')
        with self.assertRaises(utils.SeqError):
            X = bioseq.Protein().set_sequence('1234')
            X.verify_sequence()

    def test_basic_subsequence_operations(self):
        X = bioseq.DNA().set_sequence('ATCGAT')
        L = X.get_sequence_length()
        self.assertEqual(L,6)
        L = X.get_sequence_length(2,4)
        self.assertEqual(L,2)
        seq = X.get_sequence()
        self.assertEqual(seq,'ATCGAT')
        seq = X.get_sequence(2,4)
        self.assertEqual(seq,'CG')

        X.delete_sequence(start=1,end=3)
        self.assertEqual(X.sequence,'AGAT')
        X.insert_sequence('TC',start=1)
        self.assertEqual(X.sequence,'ATCGAT')
        X.delete_sequence(start=1,length=2)
        self.assertEqual(X.sequence,'AGAT')

    def test_compatibility_between_sites_and_molecules(self):
        X = bioseq.DNA().set_sequence('ATCGAT')
        f = bioseq.PolynucleotideFeature().set_molecule(X)
        self.assertEqual(f.molecule,X)
        X = bioseq.RNA().set_sequence('AUCGAU')
        f.set_molecule(X)
        self.assertEqual(f.molecule,X)
        with self.assertRaises(utils.ValidateError):
            f = bioseq.PolypeptideFeature().set_molecule(X)
            f.verify_allowed_molecule_type()

    def test_sequence_feature_setting(self):
        inputstr = 'ATCGAT'
        X = bioseq.DNA(use_permissive_alphabet=False).set_sequence(inputstr)
        f = bioseq.PolynucleotideFeature().set_molecule(X)
        f.set_location(start=1,end=3)

        # examples to show how to use PolynucleotideFeature.get_sequence()

        s = [
            X.get_sequence(start=1,end=3),
            X.get_sequence(start=1,length=2),
            X.get_sequence(1,3),
            X.get_sequence(1,None,2),
            ]
        self.assertEqual(s,['TC']*4)

        # setting feature
        f.set_location(start=1,end=3)
        s = [
            X.get_sequence(start=f.get_start(),end=f.get_end()),
            X.get_sequence(start=f.get_start(),length=f.get_length()),
            X.get_sequence(f.get_start(),f.get_end()),
            X.get_sequence(f.get_start(),None,f.get_length()),
            X.get_sequence(**f.get_location())
            ]
        self.assertEqual(s,['TC']*5)

        f.set_location(start=1,length=2)
        s = [
            X.get_sequence(start=f.get_start(),end=f.get_end()),
            X.get_sequence(start=f.get_start(),length=f.get_length()),
            X.get_sequence(f.get_start(),f.get_end()),
            X.get_sequence(f.get_start(),None,f.get_length()),
            X.get_sequence(**f.get_location())
            ]
        self.assertEqual(s,['TC']*5)

        f.set_location(1,3)
        s = [
            X.get_sequence(start=f.get_start(),end=f.get_end()),
            X.get_sequence(start=f.get_start(),length=f.get_length()),
            X.get_sequence(f.get_start(),f.get_end()),
            X.get_sequence(f.get_start(),None,f.get_length()),
            X.get_sequence(**f.get_location())
            ]
        self.assertEqual(s,['TC']*5)

        f.set_location(1,None,2)
        s = [
            X.get_sequence(start=f.get_start(),end=f.get_end()),
            X.get_sequence(start=f.get_start(),length=f.get_length()),
            X.get_sequence(f.get_start(),f.get_end()),
            X.get_sequence(f.get_start(),None,f.get_length()),
            X.get_sequence(**f.get_location())
            ]
        self.assertEqual(s,['TC']*5)

        f.set_location(0,None,6)
        s = X.get_sequence(**f.get_location())
        self.assertEqual(s,inputstr)

        f.set_location(6,None,0)
        s = X.get_sequence(**f.get_location())
        self.assertEqual(s,'')

        with self.assertRaises(utils.SeqError):
            f.set_location(-1,0)
            X.verify_location(**f.get_location())
        with self.assertRaises(utils.SeqError):
            f.set_location(0,-1)
            X.verify_location(**f.get_location())
        with self.assertRaises(utils.SeqError):
            f.set_location(6,1)
            X.verify_location(**f.get_location())
        with self.assertRaises(utils.SeqError):
            f.set_location(6,None,1)
            X.verify_location(**f.get_location())

    def test_nucleotide_sequence_conversion(self):
        inputstr = 'TTGTTATCGTTACCGGGAGTGAGGCGTCCGCGTCCCTTTCAGGTCAAGCGACTGAAAAACCTTGCAGTTGATTTTAAAGCGTATAGAAGACAATACAGA'
        X = bioseq.DNA(use_permissive_alphabet=False).set_sequence(inputstr)
        seq_list = [
        X.get_dna(0,33,option='coding'),
        X.get_dna(0,33,option='complementary'),
        X.get_dna(0,33,option='reverse_complementary'),
        X.get_rna(0,33,option='coding'),
        X.get_rna(0,33,option='complementary'),
        X.get_rna(0,33,option='reverse_complementary'),
        X.get_protein(0,33,option='coding'),
        X.get_protein(0,33,option='complementary'),
        X.get_protein(0,33,option='reverse_complementary'),
        ]
        s_list = [
        'TTGTTATCGTTACCGGGAGTGAGGCGTCCGCGT',
        'AACAATAGCAATGGCCCTCACTCCGCAGGCGCA',
        'ACGCGGACGCCTCACTCCCGGTAACGATAACAA',
        'UUGUUAUCGUUACCGGGAGUGAGGCGUCCGCGU',
        'AACAAUAGCAAUGGCCCUCACUCCGCAGGCGCA',
        'ACGCGGACGCCUCACUCCCGGUAACGAUAACAA',
        'LLSLPGVRRPR',
        'NNSNGPHSAGA',
        'TRTPHSR*R*Q',
        ]
        for (seq,s) in zip(seq_list,s_list):
            self.assertEqual(seq,s)

        inputstr = 'CGUUAAAAGCUCGGCAAUUGUUCCGAUGACGAGGCAAUGAAUAAUUACUGACUGUAACGAAUUAGGUAGCGCAGGGCCAUGCGACCCAUCAACUGCCCC'
        X = bioseq.RNA(use_permissive_alphabet=False).set_sequence(inputstr)
        seq_list = [
        X.get_dna(0,33,option='coding'),
        X.get_dna(0,33,option='complementary'),
        X.get_dna(0,33,option='reverse_complementary'),
        X.get_rna(0,33,option='coding'),
        X.get_rna(0,33,option='complementary'),
        X.get_rna(0,33,option='reverse_complementary'),
        X.get_protein(0,33,option='coding'),
        X.get_protein(0,33,option='complementary'),
        X.get_protein(0,33,option='reverse_complementary'),
        ]
        s_list = [
        'CGTTAAAAGCTCGGCAATTGTTCCGATGACGAG',
        'GCAATTTTCGAGCCGTTAACAAGGCTACTGCTC',
        'CTCGTCATCGGAACAATTGCCGAGCTTTTAACG',
        'CGUUAAAAGCUCGGCAAUUGUUCCGAUGACGAG',
        'GCAAUUUUCGAGCCGUUAACAAGGCUACUGCUC',
        'CUCGUCAUCGGAACAAUUGCCGAGCUUUUAACG',
        'R*KLGNCSDDE',
        'AIFEPLTRLLL',
        'LVIGTIAELLT',
        ]
        for (seq,s) in zip(seq_list,s_list):
            self.assertEqual(seq,s)
