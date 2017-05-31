""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""
import wc_rules.chem as chem

###### Structure Improvements ######
class Protein(chem.Molecule): pass
class ProteinSite(chem.Site): pass

###### Variable Improvements ######
class PhosphorylationState(chem.BooleanStateVariable): pass

###### Operation Improvements ######
class Phosphorylate(chem.SetTrue): pass
class Dephosphorylate(chem.SetFalse): pass


def main():
	pass
		
if __name__ == '__main__': 
	main()

