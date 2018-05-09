"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-20
:Copyright: 2017, Karr Lab
:License: MIT
"""
from obj_model import core
from wc_rules import base,entity,utils


class Molecule(entity.Entity):
    # Setters
    def add_sites(self,*args):
        self.sites.extend(args)
        return self

    # Getters
    def get_sites(self,site_type=None):
        return self.sites.get(__type=site_type)

    # Unsetters
    def remove_sites(self,*args):
        for arg in args:
            self.sites.discard(arg)
        return self

class Site(entity.Entity):
    molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
    allowed_molecule_types = None

    # Setters
    def set_molecule(self,molecule):
        self.molecule = molecule
        return self

    def add_relations_as_source(self,*relations):
        self.site_relations_sources.extend(relations)
        return self

    def add_relations_as_target(self,*relations):
        self.site_relations_targets.extend(relations)
        return self

    # Getters
    def get_molecule(self):
        return self.molecule
        
    def get_source_relations(self,relation_type=None):
        return self.site_relations_sources.get(__type=relation_type)

    def get_target_relations(self,relation_type=None):
        return self.site_relations_targets.get(__type=relation_type)

    # Unsetters
    def unset_molecule(self):
        self.molecule = None
        return self

    # Validators
    def verify_molecule_type(self):
        if not isinstance(self.molecule,self.allowed_molecule_types):
            raise utils.ValidateError('Molecule and site incompatible.')
        return

    def verify_maximum_allowed_relations_as_a_source(self):
        for relation in self.get_source_relations():
            if relation.n_max_relations_for_a_source is not None:
                if len(self.get_source_relations(relation_type=type(relation))) > relation.n_max_relations_for_a_source:
                    raise utils.ValidateError('Maximum number of relations of the same type allowed for this source site exceeded.')
        return

    def verify_maximum_allowed_relations_as_a_target(self):
        for relation in self.get_target_relations():
            if relation.n_max_relations_for_a_target is not None:
                if len(self.get_target_relations(relation_type=type(relation))) > relation.n_max_relations_for_a_target:
                    raise utils.ValidateError('Maximum number of relations of the same type allowed for this target site exceeded.')
        return

class SiteRelation(entity.Entity):
    sources = core.ManyToManyAttribute(Site,related_name='site_relations_sources')
    targets = core.ManyToManyAttribute(Site,related_name='site_relations_targets')
    n_max_sources = None
    n_max_targets = None
    n_max_relations_for_a_source = None
    n_max_relations_for_a_target = None
    allowed_source_types = None
    allowed_target_types = None

    # Setters
    def add_sources(self,*args):
        self.sources.extend(args)
        return self

    def add_targets(self,*args):
        self.targets.extend(args)
        return self

    # Getters
    def get_sources(self):
        return self.sources

    def get_targets(self):
        return self.targets

    # Unsetters
    def remove_sources(self,*args):
        for arg in args:
            self.sources.discard(arg)
        return self

    def remove_targets(self,*args):
        for arg in args:
            self.targets.discard(arg)
        return self

    # Validators
    def verify_source_types(self):
        if self.allowed_source_types is not None:
            for site in self.sources:
                if not isinstance(site,self.allowed_source_types):
                    raise utils.ValidateError('This site type is invalid as source for this relation.')
        return

    def verify_target_types(self):
        if self.allowed_target_types is not None:
            for site in self.targets:
                if not isinstance(site,self.allowed_target_types):
                    raise utils.ValidateError('This site type is invalid as target for this relation.')
        return

    def verify_maximum_sources(self):
        if self.n_max_sources is not None and len(self.sources) > self.n_max_sources:
            raise utils.ValidateError('Maximum number of sources exceeded for this relation.')
        return

    def verify_maximum_targets(self):
        if self.n_max_targets is not None and len(self.targets) > self.n_max_targets:
            raise utils.ValidateError('Maximum number of targets exceeded for this relation.')
        return

class Bond(SiteRelation):
    n_max_sources = 0
    n_max_targets = 2
    n_max_relations_for_a_source = 0
    n_max_relations_for_a_target = 1
