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
    def get_sites(self,**kwargs):
        site_type = kwargs.pop('site_type',None)
        return self.sites.get(__type=site_type,**kwargs)

    # Unsetters
    def remove_sites(self,*args):
        for arg in args:
            self.sites.discard(arg)
        return self

class Site(entity.Entity):
    molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
    allowed_molecule_types = None
    allowed_to_bind = True

    # Setters
    def set_molecule(self,molecule):
        self.molecule = molecule
        return self

    def add_interactions_as_source(self,*interactions):
        self.site_interactions_sources.extend(interactions)
        return self

    def add_interactions_as_target(self,*interactions):
        self.site_interactions_targets.extend(interactions)
        return self

    # Getters
    def get_molecule(self):
        return self.molecule

    def get_source_interactions(self,interaction_type=None):
        return self.interactions_as_sources.get(__type=interaction_type)

    def get_target_interactions(self,interaction_type=None):
        return self.interactions_as_targets.get(__type=interaction_type)

    def get_bond(self):
        bonds = self.interactions_as_targets.get(__type=Bond)
        if len(bonds)==0: return None
        if len(bonds)==1: return bonds[0]
        return

    # Unsetters
    def unset_molecule(self):
        self.molecule = None
        return self

    # Validators
    def verify_molecule_type(self):
        if not isinstance(self.molecule,self.allowed_molecule_types):
            raise utils.ValidateError('Molecule and site incompatible.')
        return

    def verify_maximum_allowed_interactions_as_a_source(self):
        for interaction in self.get_source_interactions():
            if interaction.n_max_interactions_for_a_source is not None:
                if len(self.get_source_interactions(interaction_type=type(interaction))) > interaction.n_max_interactions_for_a_source:
                    raise utils.ValidateError('Maximum number of interactions of the same type allowed for this source site exceeded.')
        return

    def verify_maximum_allowed_interactions_as_a_target(self):
        for interaction in self.get_target_interactions():
            if interaction.n_max_interactions_for_a_target is not None:
                if len(self.get_target_interactions(interaction_type=type(interaction))) > interaction.n_max_interactions_for_a_target:
                    raise utils.ValidateError('Maximum number of interactions of the same type allowed for this target site exceeded.')
        return

    def verify_allowed_to_bind(self):
        if not self.allowed_to_bind:
            raise utils.ValidateError('This site is not allowed to have a bond.')
        return

class Interaction(entity.Entity):
    sources = core.ManyToManyAttribute(Site,related_name='interactions_as_sources')
    targets = core.ManyToManyAttribute(Site,related_name='interactions_as_targets')
    n_max_sources = None
    n_max_targets = None
    n_max_interactions_for_a_source = None
    n_max_interactions_for_a_target = None
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
                    raise utils.ValidateError('This site type is invalid as source for this interaction object.')
        return

    def verify_target_types(self):
        if self.allowed_target_types is not None:
            for site in self.targets:
                if not isinstance(site,self.allowed_target_types):
                    raise utils.ValidateError('This site type is invalid as target for this interaction object.')
        return

    def verify_maximum_sources(self):
        if self.n_max_sources is not None and len(self.sources) > self.n_max_sources:
            raise utils.ValidateError('Maximum number of sources exceeded for this interaction object.')
        return

    def verify_maximum_targets(self):
        if self.n_max_targets is not None and len(self.targets) > self.n_max_targets:
            raise utils.ValidateError('Maximum number of targets exceeded for this interaction object.')
        return

class Bond(Interaction):
    n_max_sources = 0
    n_max_targets = 2
    n_max_interactions_for_a_source = 0
    n_max_interactions_for_a_target = 1
