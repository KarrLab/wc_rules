from wc_rules.chem import Molecule, Site
from obj_model.extra_attributes import *
from Bio.Seq import Seq
from Bio import SeqFeature
from numpy import full
import itertools

class SequencePropertyAttribute(NumpyArrayAttribute): pass

class SequenceMolecule(Molecule):
	seq = BioSeqAttribute()

	def add_sequence(self,seq):
		alphabet = self.Meta.attributes['seq'].alphabet
		self.seq = Seq(seq,alphabet)
		return self
	def initialize_SequencePropertyAttribute(self,attrname):
		dim = len(self.seq)
		attr = self.Meta.attributes[attrname]
		default_fill = attr.default_fill
		dtype = attr.dtype
		init_vals = full(dim,default_fill,dtype)
		setattr(self,attrname,init_vals)
		return self
		
	def initialize_properties(self):
		if self.seq is not None and len(self.seq)>0:
			for attrname,attr in self.Meta.attributes.items():
				if isinstance(attr,SequencePropertyAttribute):
					self.initialize_SequencePropertyAttribute(attrname)
		return self
		
	def sort_sites(self):
		self.sites = sorted(self.sites, key = lambda x: (x.location.start,x.location.end))
		return self
		
	def compute_overlaps(self):
		for site1,site2 in itertools.combinations(self.sites,2):
			if (site1.location.start in site2.location) or (site1.location.end in site2.location):
				site1.add_overlaps(site2)
		return self
		
	
	
class DSDNA(SequenceMolecule):
	seq = BioDnaSeqAttribute()
	binding_footprint = SequencePropertyAttribute(dtype=bool,default_fill=False)

			
class SequenceSite(Site):
	location = FeatureLocationAttribute()
	
			
def main():
	pass
	
if __name__ == '__main__': 
	main()