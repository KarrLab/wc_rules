from typedlist import TypedList

class Molecule(list): pass

class MoleculeList(TypedList): 
	def __init__(self,*args):
		super(MoleculeList,self).__init__(tuple([Molecule]),args)