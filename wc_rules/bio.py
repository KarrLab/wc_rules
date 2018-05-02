""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import chem
from wc_rules import variables

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
