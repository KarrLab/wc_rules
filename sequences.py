# Author: John Sekar
# johnarul.sekar (at) gmail (dot) com

import sys
import re
from collections import deque as dq

class BNGNucBase(object):
	"""
	Attributes:
	sugar: DNA/RNA
	type: A/T/C/G/X/U
	p5: Int or None
	p3: Int or None
	b: Int or None
	c: Int or None
	fp: 0 or 1
	"""
	p5 = None
	p3 = None
	c = None
	b = None
	fp = 0
	def __init__(self,sugar,type):
		self.sugar = sugar
		self.type = type
		return
	def __str__(self):
		s = self.sugar
		if self.type=='X' or self.type=='x': 
			t=self.getstatestr('t')
		else:
			t=self.getstatestr('t',self.type)
		p5str = self.getbondstr('p5',self.p5)
		p3str = self.getbondstr('p3',self.p3)
		cstr = self.getbondstr('c',self.c)
		bstr = self.getbondstr('b',self.b)
		fpstr = self.getstatestr('fp',self.fp)
		outstr =  s+'('+ ','.join([t,p5str,p3str,cstr,bstr,fpstr])+')'
		return outstr
		
	def __repr__(self):
		return self.__str__()
	
	@staticmethod
	def getbondstr(comp,bondnum):
		if bondnum is not None:
			return comp + '!' + str(bondnum)
		return comp
	@staticmethod
	def getstatestr(comp,state):
		if state is not None:
			return comp + '~' + str(state)
		return comp
	
class BNGNucObject(list):
	'''
	list of BNGNucBase(s)
	'''
	def __str__(self):
		temp = [x.__str__() for x in self if x is not None]
		outstr = '.'.join(temp)
		return outstr
	
	@classmethod
	def fromNucObject(cls,obj):
		seq = obj.seq
		basepairs = obj.basepairs
		
		baselist = cls([None]*len(seq))
		
		openpairs = dq()
		currentsugar = ''
		prevbase = None
		currbase = None
		prevbase = None
		bondnum = -1
		
		for i,base in enumerate(seq):
			currbase = i
			cond_D = base=='D' or base =='d'
			cond_R = base=='R' or base =='r'
			if cond_D:
				currentsugar = 'd'
				prevbase = None
				continue
			if cond_R:
				currentsugar = 'r'
				prevbase = None
				continue
			baselist[currbase] = BNGNucBase(currentsugar,base)
			if prevbase is not None:
				bondnum = bondnum + 1
				baselist[prevbase].p3 = bondnum
				baselist[currbase].p5 = bondnum
			if basepairs[i]=='(':
				openpairs.append(i)
			elif basepairs[i]==')':
				bondnum = bondnum + 1
				baselist[openpairs.pop()].c = bondnum
				baselist[i].c = bondnum
			else:
				pass
			prevbase = currbase
		return baselist
		
		
class NucObject(object):
	""" A nucleotide object. Could be a combination of many base-pairing strands.
		seq: string
		basepairs: string
		
		Sequence should be of the form
			dACGXUrAXUCG
		where d,r begin a DNA/RNA strand, and ATCGXU are elements of the strand arranged 5'-3'.
		
		Basepairs should be of the same length as Sequence and should be of the form
			(((....)))
		where ( and ) denote complementary base pairs, and . denotes no base pairing.
	"""
	
	def __init__(self,seq,basepairs=None):
		self.seq = seq
		if basepairs==None :
			self.basepairs = '.'*len(seq)
		else:
			self.basepairs = basepairs
		return
	
	@classmethod
	def fromfile(cls,file):
		'''Makes a nucleotide object from a file.'''	
		lines = []
		with open(file,'r') as f:
			lines = f.readlines()
		lines = [x.strip().rstrip('\r\n') for x in lines]
		nuc =  cls(lines[0],lines[1])
		if nuc.verify()==False:
			nuc = None
		return nuc
		
	def __str__(self):
		return self.seq+"\n"+self.basepairs

	def verify(self):
		return verifyNucleotideObject(self.seq,self.basepairs)
		
	def toGML(self,filename):
		outstr = makeGMLString(self.seq,self.basepairs)
		f=open(filename,'w')
		f.write(outstr)
		f.close()
		return 
		
	
def makeGMLString(seq,basepairs):
	baselist = [None]*len(seq)
	openpairs = dq()
	currentsugar = ''
	prevbase = None
	currbase = None
	idnum = -1
	sugarbonds = []
	pairbonds = []
	for i,base in enumerate(seq):
		currbase = i
		if base=='D' or base =='d' or base=='R' or base =='r':
			currentsugar = base.lower()
			prevbase = None
			baselist[i] = None
			continue
		
		name = currentsugar + base.upper()
		idnum = idnum + 1
		baselist[currbase] = {'name':name,'id':idnum}
		if prevbase is not None:
			x = baselist[prevbase]
			y = baselist[currbase]
			sugarbonds.append((x['id'],y['id']))
		if basepairs[i]=='(':
			openpairs.append(i)
		elif basepairs[i]==')':
			x = baselist[openpairs.pop()]
			y = baselist[i]
			pairbonds.append((x['id'],y['id']))
		else:
			pass
		prevbase = currbase
		
	nodes = [nodestring(x) for x in baselist if x is not None]
	edges1 = [edgestring(x[0],x[1],True,False) for x in sugarbonds]
	edges2 = [edgestring(x[0],x[1],False,True) for x in pairbonds]
	outstr = graphstring(nodes+edges1+edges2)
	return outstr
		
def nodestring(node):
	idstr = "id "+str(node['id'])
	labelstr = "label \""+node['name']+"\""
	colordict = {'A':'#fb8072','T':'#bebada','U':'#bebada',
	'C':'#ffffb3','G':'#8dd3c7','X':'#999999'}
	fillstr = "fill \""+colordict[node['name'][1]]+"\""
	typestr = "type \"ellipse\""
	outlinestr = "outline \"#999999\""
	graphics = " ".join(["graphics","[",typestr,fillstr,outlinestr,"]"])
	outstr = " ".join(["node", "[", idstr,labelstr,graphics,"]"])
	return outstr

def edgestring(source,target,directed=False,dashed=False):
	sourcestr = "source " + str(source)
	targetstr = "target " + str(target)
	fillstr = "fill \"#999999\""
	sourceArrow = "sourceArrow \"none\""
	if directed:
		targetArrow = "targetArrow \"standard\""
	else:
		targetArrow = "targetArrow \"none\""
	if dashed:
		style = "style \"dashed\""
	else:
		style = "style \"line\""
	graphics = " ".join(["graphics","[",fillstr,style,sourceArrow,targetArrow,"]"])
	outstr = " ".join(["edge","[",sourcestr,targetstr,graphics,"]"])
	return outstr
	
def graphstring(strings):
	strs = ["graph","[","directed 1"] + strings + ["]"]
	return "\n".join(strs)
	
	
		
def verifyNucleotideObject(seq,basepairs):
	cond01 = len(seq)==len(basepairs)
	if not cond01:
		print "Sequence length not the same as basepair notation length."
		return False
	cond02 = re.search(r'([^ATCGXUatcgxuDRdr])',seq)
	if cond02 is not None:
		print "Unexpected character found in sequence:", cond02.group(0)
		return False
	cond03 = re.search(r'([^\(\)\.])',basepairs)
	if cond03 is not None:
		print "Unexpected character found in base-pair notation:", cond03.group(0)
		return False
	cond04 = seq[0]=='D' or seq[0]=='d' or seq[0]=='R' or seq[0]=='r'
	if not cond04:
		print "Sequence must begin with one of [DdRr] characters to indicate DNA/RNA strand."
		return False
	numleft = len(re.findall(r'\(',basepairs))
	numright = len(re.findall(r'\)',basepairs))
	if numleft != numright :
		print "Unmatched brackets in base-pair notation."
		return False
	return True
		
	
		
if __name__ == '__main__':
	if len(sys.argv) > 1:
		file = sys.argv[1]
		a = NucObject.fromfile(file)
		a.toGML('a.gml')
		
	
	