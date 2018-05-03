""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-02
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import seq,utils
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA,IUPACUnambiguousDNA,IUPACAmbiguousRNA,IUPACUnambiguousRNA,IUPACProtein,ExtendedIUPACProtein

###### Sequence Objects ######
class Polynucleotide(seq.SequenceMolecule):pass

class PolynucleotideFeature(seq.SequenceFeature):
    allowed_molecule_types = (Polynucleotide,)

    def get_complement(self,sequence=None):
        if sequence is None:
            sequence = self.get_sequence()
        return sequence.complement()

    def get_reverse(self,sequence=None):
        if sequence is None:
            sequence = self.get_sequence()
        return sequence[::-1]

    def get_reverse_complement(self,sequence=None):
        if sequence is None:
            sequence = self.get_sequence()
        return self.get_reverse(sequence=self.get_complement())

    def convert_to(self,nucleotide_type,sequence=None):
        if sequence is None:
            sequence=self.get_sequence()
        if nucleotide_type == 'rna':
            return sequence.transcribe()
        if nucleotide_type == 'dna':
            return sequence.back_transcribe()
        raise utils.SeqError('Improper use of convert_to')
        return

class DNA(Polynucleotide):
    alphabet_dict = {'unambiguous':IUPACUnambiguousDNA(),'ambiguous':IUPACAmbiguousDNA()}

class RNA(Polynucleotide):
    alphabet_dict = {'unambiguous':IUPACUnambiguousRNA(),'ambiguous':IUPACAmbiguousRNA()}

class Polypeptide(seq.SequenceMolecule):
    alphabet_dict = {'unambiguous':IUPACProtein(),'ambiguous':ExtendedIUPACProtein()}
class PolypeptideFeature(seq.SequenceFeature):
    allowed_molecule_types = (Polypeptide,)

class Protein(Polypeptide):pass
