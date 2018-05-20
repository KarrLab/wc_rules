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
    def add_sites(self,*sites):
        self.sites.extend(sites)
        return self

    # Getters
    def get_sites(self,**kwargs):
        site_type = kwargs.pop('site_type',None)
        return self.sites.get(__type=site_type,**kwargs)

    # Unsetters
    def remove_sites(self,*sites):
        for site in sites:
            self.sites.discard(site)
        return self

class Site(entity.Entity):
    molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
    allowed_molecule_types = None
    allowed_to_bind = True

    # Setters
    def set_molecule(self,molecule):
        self.molecule = molecule
        return self

    def set_bond(self,bond):
        self.bond = bond
        return self

    def add_overlaps(self,*overlaps):
        self.overlaps.extend(overlaps)
        return

    # Getters
    def get_molecule(self):
        return self.molecule

    def get_bond(self):
        return self.bond

    def get_overlaps(self,**kwargs):
        return self.overlaps.get(**kwargs)

    # Unsetters
    def unset_molecule(self):
        self.molecule = None
        return self

    def unset_bond(self):
        self.bond = None
        return self

    def remove_overlaps(self,*overlaps):
        for overlap in overlaps:
            self.overlaps.discard(overlap)
        return self

    # Validators
    def verify_allowed_molecule_type(self):
        if not isinstance(self.molecule,self.allowed_molecule_types):
            raise utils.ValidateError('Molecule and site incompatible.')
        return

    def verify_allowed_to_bind(self):
        if not self.allowed_to_bind:
            raise utils.ValidateError('This site is not allowed to have a bond.')
        return

class Bond(entity.Entity):
    sites = core.OneToManyAttribute(Site,related_name='bond')
    allowed_site_types = None
    n_max_sites = 2

    # Setters
    def add_sites(self,*sites):
        self.sites.extend(sites)
        return self

    # Unsetters
    def remove_sites(self,*sites):
        for site in sites:
            self.sites.discard(site)
        return self

    # Getters
    def get_sites(self,**kwargs):
        return self.sites.get(**kwargs)

    def get_number_of_sites(self):
        return len(self.sites)

    # Validators
    def verify_allowed_site_types(self):
        for site in self.sites:
            if self.allowed_site_types is not None:
                if not isinstance(site,self.allowed_site_types):
                    raise utils.ValidateError('Bond and site incompatible.')
        return

    def verify_maximum_number_of_sites(self):
        if self.n_max_sites is not None:
            if len(self.sites) > self.n_max_sites:
                raise utils.ValidateError('Maximum number of allowed sites exceeds n_max_sites.')
        return

class Overlap(entity.Entity):
    sites = core.ManyToManyAttribute(Site,related_name='overlaps')

    # Setters
    def add_sites(self,*sites):
        self.sites.extend(sites)
        return self

    # Unsetters
    def remove_sites(self,*sites):
        for site in sites:
            self.sites.discard(site)
        return self

    # Getters
    def get_sites(self,**kwargs):
        return self.sites.get(**kwargs)
