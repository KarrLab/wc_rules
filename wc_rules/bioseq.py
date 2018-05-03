""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-02
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import seq
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA,IUPACUnambiguousDNA,IUPACAmbiguousRNA,IUPACUnambiguousRNA,IUPACProtein,ExtendedIUPACProtein

###### Sequence Objects ######
class Polynucleotide(seq.SequenceMolecule):pass
class PolynucleotideFeature(seq.SequenceFeature):
    allowed_molecule_types = (Polynucleotide,)

class DNA(Polynucleotide):
    alphabet_dict = {'unambiguous':IUPACUnambiguousDNA(),'ambiguous':IUPACAmbiguousDNA()}

class RNA(Polynucleotide):
    alphabet_dict = {'unambiguous':IUPACUnambiguousRNA(),'ambiguous':IUPACAmbiguousRNA()}

class Polypeptide(seq.SequenceMolecule):
    alphabet_dict = {'unambiguous':IUPACProtein(),'ambiguous':ExtendedIUPACProtein()}
class PolypeptideFeature(seq.SequenceFeature):
    allowed_molecule_types = (Polypeptide,)

class Protein(Polypeptide):pass
