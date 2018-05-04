"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-20
:Copyright: 2017, Karr Lab
:License: MIT
"""
from obj_model import core
from wc_rules import base,entity,utils


class Molecule(entity.Entity):
    def add_sites(self,*args,force=False):
        if not force:
            for arg in args:
                arg._verify_site_molecule_compatibility(molecule=self)
        self.sites.extend(args)
        return self

class Site(entity.Entity):
    molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
    allowed_molecule_types = None

    def _verify_site_molecule_compatibility(self,molecule):
        if self.allowed_molecule_types is not None:
            if type(self.allowed_molecule_types) is tuple:
                classes = self.allowed_molecule_types
            else:
                classes = tuple(utils.listify(self.allowed_molecule_types))
            if not isinstance(molecule,classes):
                raise utils.AddError('Incompatible molecule and site.')
        return True

    def _get_number_of_source_relations(self, relation_type=None):
        if self.site_relations_sources is not None:
            return len(self.site_relations_sources.get(__type=relation_type))
        return 0
    def _get_number_of_target_relations(self, relation_type=None):
        if self.site_relations_targets is not None:
            return len(self.site_relations_targets.get(__type=relation_type))
        return 0

    def set_molecule(self,molecule):
        self._verify_site_molecule_compatibility(molecule)
        self.molecule = molecule
        return self

class SiteRelation(entity.Entity):
    sources = core.ManyToManyAttribute(Site,related_name='site_relations_sources')
    targets = core.ManyToManyAttribute(Site,related_name='site_relations_targets')
    n_max_sources = None
    n_max_targets = None
    n_max_relations_for_a_source = None
    n_max_relations_for_a_target = None

    def verify_add_sources(self,*args):
        if self.n_max_sources is not None:
            if len(self.sources)+len(args) > self.n_max_sources:
                raise utils.AddError('Number of source sites allowed for '+str(type(self))+ ' relation must not exceed ' + str(self.n_max_sources)+'.')
        if self.n_max_relations_for_a_source is not None:
            for arg in args:
                n_existing = arg._get_number_of_source_relations(type(self))
                if n_existing + 1 > self.n_max_relations_for_a_source:
                    raise utils.AddError('Source site already has the allowed maximum of '+str(type(self))+ ' relations: ' + str(self.n_max_relations_for_a_source)+'.')
        return True

    def verify_add_targets(self,*args):
        if self.n_max_targets is not None:
            if len(self.targets)+len(args) > self.n_max_targets:
                raise utils.AddError('Number of target sites allowed for '+str(type(self))+ ' relation must not exceed ' + str(self.n_max_targets)+'.')
        if self.n_max_relations_for_a_target is not None:
            for arg in args:
                n_existing = arg._get_number_of_target_relations(type(self))
                if n_existing + 1 > self.n_max_relations_for_a_target:
                    raise utils.AddError('Target site already has the allowed maximum of '+str(type(self))+ ' relations: ' + str(self.n_max_relations_for_a_target)+'.')
        return True

    def add_sources(self,*args):
        if self.verify_add_sources(*args):
            self.sources.extend(args)
        return self

    def add_targets(self,*args):
        if self.verify_add_targets(*args):
            self.targets.extend(args)
        return self

class Bond(SiteRelation):
    n_max_sources = 0
    n_max_targets = 2
    n_max_relations_for_a_source = 0
    n_max_relations_for_a_target = 1
