""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import chem
from wc_rules import variables
from wc_rules import seq
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA,IUPACUnambiguousDNA,IUPACAmbiguousRNA,IUPACUnambiguousRNA,IUPACProtein,ExtendedIUPACProtein

###### Sequence Objects ######
class DNASequenceMolecule(seq.SequenceMolecule):
    alphabet_dict = {'unambiguous':IUPACUnambiguousDNA(),'ambiguous':IUPACAmbiguousDNA()}

class RNASequenceMolecule(seq.SequenceMolecule):
    alphabet_dict = {'unambiguous':IUPACUnambiguousRNA(),'ambiguous':IUPACAmbiguousRNA()}

class ProteinSequenceMolecule(seq.SequenceMolecule):
    alphabet_dict = {'unambiguous':IUPACProtein(),'ambiguous':ExtendedIUPACProtein()}

###### Structure Improvements ######
class Protein(chem.Molecule):
    pass

class ProteinSite(chem.Site):
    pass

###### Variable Improvements ######
class PhosphorylationState(variables.BooleanVariable):
    pass

###### Operation Improvements ######
class Phosphorylate(chem.SetTrue):
    pass

class Dephosphorylate(chem.SetFalse):
    pass
