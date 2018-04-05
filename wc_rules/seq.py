"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import chem
from wc_rules import utils
from obj_model import extra_attributes
import Bio.Seq
import Bio.Alphabet
import itertools
import numpy

class SequenceMolecule(chem.Molecule):
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


    #class SequencePropertyAttribute(extra_attributes.NumpyArrayAttribute):
    #    pass


    # def add_sequence(self, seq, seqtype, unambiguous=False):
    #     alphabet = self.Meta.attributes['seq'].alphabet
    #     self.seq = Bio.Seq.Seq(seq, self.alphabet)
    #     return self
    #
    # def initialize_SequencePropertyAttribute(self, attrname):
    #     dim = len(self.seq)
    #     attr = self.Meta.attributes[attrname]
    #     default_fill = attr.default_fill
    #     dtype = attr.dtype
    #     init_vals = numpy.full(dim, default_fill, dtype)
    #     setattr(self, attrname, init_vals)
    #     return self
    #
    # def initialize_properties(self):
    #     if self.seq is not None and len(self.seq) > 0:
    #         for attrname, attr in self.Meta.attributes.items():
    #             if isinstance(attr, SequencePropertyAttribute):
    #                 self.initialize_SequencePropertyAttribute(attrname)
    #     return self

    # def sort_sites(self):
    #     self.sites = sorted(self.sites, key=lambda x: (x.location.start, x.location.end))
    #     return self
    #
    # def compute_overlaps(self):
    #     for site1, site2 in itertools.combinations(self.sites, 2):
    #         if (site1.location.start in site2.location) or (site1.location.end in site2.location):
    #             site1.add_overlaps(site2)
    #     return self
    #
    #        binding_footprint = SequencePropertyAttribute(dtype=bool, default_fill=False)
    #



class SequenceSite(chem.Site):
    location = extra_attributes.FeatureLocationAttribute()
