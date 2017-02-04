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
		
	def __init__(self,file,id=None,circular=False):
		record = SeqIO.read(file,"fasta")
		self.seq = record.seq
		self.id = id
		self.circular = circular
		return
		
	def __repr__(self):
		return "Chromosome object\n seq=%s\n id=%s\n circular=%s" % (self.seq.__repr__(),self.id,self.circular)
		
		

if __name__ == '__main__':
	pass

	