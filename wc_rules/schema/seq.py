from . import chem
from .attributes import StringAttribute, IntegerAttribute, computation
from Bio.Seq import Seq

class SequenceMolecule(chem.Molecule):
	sequence = StringAttribute()

	@computation
	def get_sequence(sequence,start=None,end=None):
		return sequence[start:end]

	@computation
	def overlaps(start1=None,end1=None,start2=None,end2=None):
		return (start1 <= start2 < end1) or (start1 < end2 <= end1) or \
		(start2 <= start1 < end2) or (start2 <= end1 <= end2)

class SequenceFeature(chem.Site):
	start = IntegerAttribute()
	end = IntegerAttribute()


class DNA(SequenceMolecule):
	pass

class RNA(SequenceMolecule):
	pass

class PolynucleotideFeature(SequenceFeature):
	pass

