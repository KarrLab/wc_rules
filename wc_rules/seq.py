"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import base,chem2,utils
from obj_model import core,extra_attributes
import Bio.Seq
import Bio.SeqFeature
import Bio.Alphabet


class SequenceMolecule(chem2.Molecule):
    """ Generic SequenceMolecule (template for DNA, RNA, protein sequence objects) """

    sequence = extra_attributes.BioSeqAttribute()
    alphabet_dict = { 'unambiguous': None, 'ambiguous': None }

    def _get_alphabet(self, ambiguous=True):
        if ambiguous:
            a= self.alphabet_dict['ambiguous']
        else:
            a= self.alphabet_dict['unambiguous']
        return a

    def _verify_string(self, inputstr, alphabet, ambiguous=True):
        invalid_chars = [char for char in inputstr if char not in alphabet.letters]
        invalid_chars_uniq = ''
        for char in invalid_chars:
            if char not in invalid_chars_uniq:
                invalid_chars_uniq += char
        n_invalids = len(invalid_chars)
        if n_invalids > 0:
            n = str(n_invalids)
            err_str = n + ' instances of invalid characters (' + invalid_chars_uniq + ') found. Valid ' + str(alphabet) + ' characters are ' + alphabet.letters
            raise utils.SeqError(err_str)
        return True

    def init_sequence(self, inputstr = '', ambiguous = True):
        """ Initialize sequence of an empty SequenceMolecule object """
        alphabet = self._get_alphabet(ambiguous)
        if self._verify_string(inputstr, alphabet, ambiguous):
            self.sequence = Bio.Seq.Seq(inputstr, alphabet)
        return self

    def get_sequence_length(self): return len(self.sequence)
    def extract_sequence(self,featurelocation=None,position=0,length=1):
        '''Extracts a sequence given a feature location OR a start and an end.'''
        if featurelocation is not None:
            return featurelocation.extract(self.sequence)
        else:
            return self.sequence[position:position+length]
        return self.sequence

class SequenceFeature(chem2.Site):
    ''' Simple sequence feature with position index and length.
    Example:
        If parent molecule is .A.T.C.G.A.T.,
        feature with position=0,length=0 has sequence ''
        feature with position=0,length=1 has sequence 'A'
        feature with position=0,length=6 has sequence 'ATCGAT'
        feature with position=5,length=1 has sequence 'T'
        feature with position=6,length=0 has sequence ''
    '''

    position = core.IntegerAttribute(default=0,min=0)
    length = core.IntegerAttribute(default=0,min=0)

    def _get_feature_location_object(self):
        return Bio.SeqFeature.FeatureLocation(self.position, self.position + self.length)

    def _verify_site_molecule_compatibility(self,molecule):
        check = super()._verify_site_molecule_compatibility(molecule)
        if check and self._verify_feature(molecule,self.position,self.length):
            return True
        return False

    def _verify_feature(self,molecule,position=None,length=None):
        if position is not None and position < 0:
            raise utils.SeqError('Position cannot be negative.')
        if length is not None and length < 0:
            raise utils.SeqError('Length cannot be negative.')
        check_length = molecule.get_sequence_length()
        check = True
        if position is None:
            if length is not None:
                check = length <= check_length
        else:
            if length is None:
                check = position <= check_length
            else:
                check = position + length <= check_length
        if not check:
            raise utils.SeqError('Feature position/length incompatible with parent sequence.')
        return True

    def set_position(self,position,force=False):
        if not force:
            if self.molecule is not None:
                if self.length is not None:
                    self._verify_feature(self.molecule,position,self.length)
                else:
                    self._verify_feature(self.molecule,position)
        self.position = position
        return self

    def set_length(self,length,force=False):
        if not force:
            if self.molecule is not None:
                if self.position is not None:
                    self._verify_feature(self.molecule,self.position,length)
                else:
                    self._verify_feature(self.molecule,None,length)
        self.length = length
        return self

    def set_position_and_length(self,position,length):
        if self.molecule is not None:
            self._verify_feature(self.molecule,position,length)
        self.set_position(position,force=True)
        self.set_length(length,force=True)
        return self

    def get_sequence(self):
        feature_location = self._get_feature_location_object()
        return feature_location.extract(self.molecule.sequence)
