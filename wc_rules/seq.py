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
import itertools
import numpy

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

    def add_feature(self,*args):
        for arg in args:
            self.sites.append(arg)
        return self

    def sequence_length(self): return len(self.sequence)
    def extract_sequence(self,featurelocation=None,position=0,length=1):
        '''Extracts a sequence given a feature location OR a start and an end.'''
        if featurelocation is not None:
            return featurelocation.extract(self.sequence)
        else:
            return self.sequence[position:position+length]
        return self.sequence

class GenericSequenceFeature(chem2.Site):
    ''' Generic Sequence Feature, template for DNA, RNA, protein sequence features.'''

    def set_molecule(self,molecule):
        molecule.add_feature(self)
        return self

    def _get_feature_location_object(self):
        '''Returns a SeqFeature.FeatureLocation or CompoundLocation object.
        All subclasses of GenericSequenceFeature must implement this method.'''
        pass

    def _verify_feature(self):
        '''Returns True if feature is well-definedself.
        All subclasses of GenericSequenceFeature must implement this method.'''
        pass

    def get_sequence(self):
        '''Extracts sequence from parent molecule.'''
        f1 = self._get_feature_location_object()
        return f1.extract(self.molecule.sequence)

class SimpleSequenceFeature(GenericSequenceFeature):
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

    def _verify_feature(self):
        if self.position < 0 or self.length < 0:
            raise utils.SeqError('Feature position and length cannot be negative.')
        if self.position > self.molecule.sequence_length():
            raise utils.SeqError('Feature position not in range of parent molecule.')
        if self.length > self.molecule.sequence_length() - self.position:
            raise utils.SeqError('Feature length not in range of parent molecule.')
        return True

    def set_position_and_length(self,position=0,length=0):
        self.position = position
        self.length = length
        self._verify_feature()
        return self

class CompositeSequenceFeature(GenericSequenceFeature):
    ''' Is a set of features on the same molecule.'''
    features = core.OneToManyAttribute(SimpleSequenceFeature)

    def _get_feature_location_object(self):
        return sum([Bio.SeqFeature.FeatureLocation(x.position, x.position + x.length) for x in self.features])

    def _verify_feature(self):
        for feature in self.features:
            if feature.molecule is not self.molecule:
                raise utils.SeqError('Composite feature must be on same molecule as its component features.')
            feature._verify_feature()
        return True

    def add_feature(self,*args):
        for arg in args:
            if arg.molecule is not self.molecule:
                raise utils.SeqError('Composite sequence feature must have the same `molecule` attribute as its individual sequence features.')
            arg._verify_feature()
            self.features.append(arg)
        return self

class LeftOverlap(chem2.DirectedSiteRelation):
    n_max_sources = 1

class RightOverlap(chem2.DirectedSiteRelation):
    n_max_sources = 1
