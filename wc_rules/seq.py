"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""
from . import rete_nodes as rn
from . import chem, utils
from obj_tables import core
from obj_tables.bio import seq
import Bio.Seq
import Bio.Alphabet

class SequenceMolecule(chem.Molecule):
    """ Generic SequenceMolecule (template for DNA, RNA, protein sequence objects) """

    sequence = seq.SeqAttribute()
    alphabet_dict = { 'strict': None, 'permissive': None }
    use_permissive_alphabet = True
    alphabet = None

    # Static methods
    @staticmethod
    def resolve_start_end_length(start=None,end=None,length=None):
        if all([end is None,start is None,length is not None]):
            end = length
        if all([end is None,start is not None,length is not None]):
            end = start + length
        return (start,end)

    # Setters
    def __init__(self,*args,**kwargs):
        self.use_permissive_alphabet = True if kwargs.pop('use_permissive_alphabet',True) else False
        super(SequenceMolecule,self).__init__(*args,**kwargs)
        self.load_alphabet(self.use_permissive_alphabet)
        return

    def load_alphabet(self,permissive=True):
        self.alphabet = self.alphabet_dict['permissive'] if permissive else self.alphabet_dict['strict']
        return self

    def set_sequence(self, init_str = ''):
        if isinstance(init_str,Bio.Seq.Seq):
            init_str = str(init_str)
        self.sequence = Bio.Seq.Seq(init_str.upper(),self.alphabet)
        return self

    def replace_sequence(self,start=None,end=None,length=None,sequence=''):
        (start,end) = self.resolve_start_end_length(start,end,length)
        self.sequence = self.sequence[:start] + Bio.Seq.Seq(sequence.upper(),self.alphabet) + self.sequence[end:]
        return self

    def delete_sequence(self,start=None,end=None,length=None):
        self.replace_sequence(start=start,end=end,length=length,sequence='')
        return self

    def insert_sequence(self,start=None,sequence=''):
        self.replace_sequence(start=start,length=0,sequence=sequence)
        return self

    # Getters
    def get_alphabet(self,as_string=False):
        if as_string:
            return self.alphabet.letters
        return self.alphabet

    def get_sequence(self,start=None,end=None,length=None,as_string=False):
        (start,end) = self.resolve_start_end_length(start,end,length)
        if as_string:
            return str(self.sequence[start:end])
        return self.sequence[start:end]

    def get_sequence_length(self,start=None,end=None):
        return len(self.sequence[start:end])

    # Validators
    def verify_sequence(self,start=None,end=None,length=None):
        sequence = self.get_sequence(start=start,end=end,length=length)
        invalid_chars = ''.join(sorted(list(set(sequence) - set(self.alphabet.letters))))
        if len(invalid_chars) > 0:
            raise utils.SeqError('Invalid characters found: ' + invalid_chars)
        return

    def verify_location(self,start=None,end=None):
        L = self.get_sequence_length()
        if not 0 <= start <= end <= L:
            raise utils.SeqError('Start/end must be in range [0,L], where L is sequence length.')
        return


class SequenceFeature(chem.Site):
    ''' Simple sequence feature with position index and length.
    Example:
        If parent molecule is .A.T.C.G.A.T.,
        feature with start=0,end=0 has sequence ''
        feature with start=0,end=1 has sequence 'A'
        feature with start=0,end=6 has sequence 'ATCGAT'
        feature with start=5,end=6 has sequence 'T'
        feature with start=6,end=0 has sequence ''
    '''

    start = core.IntegerAttribute(default=None,min=0)
    end = core.IntegerAttribute(default=None,min=0)

    # Setters
    def set_location(self,start=None,end=None,length=None):
        if end is None:
            end = start + length
        self.start = start
        self.end = end
        return self

    # Getters
    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_length(self):
        return self.end - self.start

    def get_location(self):
        return dict(start=self.start,end=self.end)
