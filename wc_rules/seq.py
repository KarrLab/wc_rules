from wc_rules.chem import Molecule, Site
from obj_model.extra_attributes import *
from Bio.Seq import Seq

class SequencePropertyAttribute(NumpyArrayAttribute): pass

class SequenceMolecule(Molecule):
	seq = BioSeqAttribute()

	def __init__(self,**kwargs):
		super(SequenceMolecule,self).__init__(**kwargs) 
		if self.seq is not None and len(self.seq)>0:
			for attrname,attr in self.Meta.attributes.items():
				if isinstance(attr,SequencePropertyAttribute):
					setattr(self,attrname,attr.get_default(self,length=len(self.seq)))
					
			
class DSDNA(SequenceMolecule):
	seq = BioDnaSeqAttribute()
	binding_footprint = SequencePropertyAttribute(dtype=bool,default_fill=False)
	strand_break = SequencePropertyAttribute(dtype=bool,default_fill=False)

			
			
def main():
	pass
	
if __name__ == '__main__': 
	main()