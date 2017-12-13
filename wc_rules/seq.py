"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import chem
from obj_model import extra_attributes
import Bio.Seq
import itertools
import numpy


class SequencePropertyAttribute(extra_attributes.NumpyArrayAttribute):
    pass


class SequenceMolecule(chem.Molecule):
    seq = extra_attributes.BioSeqAttribute()

    def add_sequence(self, seq):
        alphabet = self.Meta.attributes['seq'].alphabet
        self.seq = Bio.Seq.Seq(seq, alphabet)
        return self

    def initialize_SequencePropertyAttribute(self, attrname):
        dim = len(self.seq)
        attr = self.Meta.attributes[attrname]
        default_fill = attr.default_fill
        dtype = attr.dtype
        init_vals = numpy.full(dim, default_fill, dtype)
        setattr(self, attrname, init_vals)
        return self

    def initialize_properties(self):
        if self.seq is not None and len(self.seq) > 0:
            for attrname, attr in self.Meta.attributes.items():
                if isinstance(attr, SequencePropertyAttribute):
                    self.initialize_SequencePropertyAttribute(attrname)
        return self

    def sort_sites(self):
        self.sites = sorted(self.sites, key=lambda x: (x.location.start, x.location.end))
        return self

    def compute_overlaps(self):
        for site1, site2 in itertools.combinations(self.sites, 2):
            if (site1.location.start in site2.location) or (site1.location.end in site2.location):
                site1.add_overlaps(site2)
        return self


class DSDNA(SequenceMolecule):
    seq = extra_attributes.BioDnaSeqAttribute()
    binding_footprint = SequencePropertyAttribute(dtype=bool, default_fill=False)


class SequenceSite(chem.Site):
    location = extra_attributes.FeatureLocationAttribute()
