# Author: John Sekar
# johnarul.sekar (at) gmail (dot) com
import sys
from Bio import SeqIO
from Bio.Seq import Seq

class Chromosome(object):
	"""
	Attributes	
		seq = Biopython Seq object
		id = unique id
	"""
	seq = None
	id = None
	circular = False
		
	def __init__(self,seq,id=None,circular=False,):
		self.seq = seq
		self.id = id
		self.circular = True
		
	@staticmethod
	def loadFasta(file,id=None,circular=False):
		record = SeqIO.read(file,"fasta")
		return Chromosome(seq = record.seq,id=id,circular=circular)
		
	def __repr__(self):
		return "Chromosome(seq=%s,id=%s,circular=%s)" % (self.seq.__repr__(),self.id,self.circular)
		
		

if __name__ == '__main__':
	pass

	