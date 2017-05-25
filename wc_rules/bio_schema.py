""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import mol_schema

###### Structures ######
class Protein(mol_schema.Molecule):
    """ Protein molecule """
    pass


class ProteinSite(mol_schema.Site):
    """ Protein site """
    pass


###### Variables ######
class PhosphorylationState(mol_schema.BooleanStateVariable):
    """ Phosphorylation state """
    pass


###### Operations ######
class Phosphorylate(mol_schema.SetTrue):
    """ Phosphorylate operation """
    pass


class Dephosphorylate(mol_schema.SetFalse):
    """ Dephosphorylate operation """
    pass
