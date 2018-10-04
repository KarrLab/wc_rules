""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-02
:Copyright: 2017, Karr Lab
:License: MIT
"""

from . import seq,utils
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA,IUPACUnambiguousDNA,IUPACAmbiguousRNA,IUPACUnambiguousRNA,IUPACProtein,ExtendedIUPACProtein

###### Sequence Objects ######
class Polynucleotide(seq.SequenceMolecule):

    def convert_sequence(self,start=None,end=None,length=None,option='coding'):
        seq = self.get_sequence(start=start,end=end,length=length)
        if option=='coding':
            x = seq
        elif option=='complementary':
            x = seq.complement()
        elif option=='reverse_complementary':
            x = seq.complement()[::-1]
        else:
            raise utils.SeqError('''convert_sequence() must use kwarg option='coding'|'complementary'|'reverse_complementary'. ''')
        return x

    def translate(self,start=None,end=None,length=None,option='coding',table=1,to_stop=False):
        seq = self.convert_sequence(start=start,end=end,length=length,option=option)
        x = seq.translate(table=table,to_stop=to_stop)
        return x

class DNA(Polynucleotide):
    alphabet_dict = {'strict':IUPACUnambiguousDNA(),'permissive':IUPACAmbiguousDNA()}

    def get_dna(self,*args,**kwargs):
        as_string = kwargs.pop('as_string',False)
        x = self.convert_sequence(*args,**kwargs)
        if as_string:
            return str(x)
        return x

    def get_rna(self,*args,**kwargs):
        as_string = kwargs.pop('as_string',False)
        x = self.convert_sequence(*args,**kwargs).transcribe()
        if as_string:
            return str(x)
        return x

    def get_protein(self,*args,**kwargs):
        as_string = kwargs.pop('as_string',False)
        x = self.translate(*args,**kwargs)
        if as_string:
            return str(x)
        return x

class RNA(Polynucleotide):
    alphabet_dict = {'strict':IUPACUnambiguousRNA(),'permissive':IUPACAmbiguousRNA()}

    def get_dna(self,*args,**kwargs):
        return self.convert_sequence(*args,**kwargs).back_transcribe()

    def get_rna(self,*args,**kwargs):
        return self.convert_sequence(*args,**kwargs)

    def get_protein(self,*args,**kwargs):
        return self.translate(*args,**kwargs)

class PolynucleotideFeature(seq.SequenceFeature):
    allowed_molecule_types = (Polynucleotide,)

class Polypeptide(seq.SequenceMolecule):
    alphabet_dict = {'strict':IUPACProtein(),'permissive':ExtendedIUPACProtein()}
class PolypeptideFeature(seq.SequenceFeature):
    allowed_molecule_types = (Polypeptide,)

class Protein(Polypeptide):pass
