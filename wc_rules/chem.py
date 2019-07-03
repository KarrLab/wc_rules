"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-20
:Copyright: 2017, Karr Lab
:License: MIT
"""
from obj_model import core
from . import base,entity,utils
from .attributes import *


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
    molecule = ManyToOneAttribute(Molecule,related_name='sites')
    bond = OneToOneAttribute('Site',related_name='bond')
    '''
    allowed_molecule_types = None
    allowed_to_bind = True
    '''
    # Setters
    def set_molecule(self,molecule):
        self.molecule = molecule
        return self

    def set_bond(self,bond):
        self.bond = bond
        return self
    '''
    def add_overlaps(self,*overlaps):
        self.overlaps.extend(overlaps)
        return
    '''
    # Getters
    def get_molecule(self):
        return self.molecule

    def get_bond(self):
        return self.bond
    '''
    def get_overlaps(self,**kwargs):
        return self.overlaps.get(**kwargs)
    '''
    # Unsetters
    def unset_molecule(self):
        self.molecule = None
        return self

    def unset_bond(self):
        self.bond = None
        return self
    '''
    def remove_overlaps(self,*overlaps):
        for overlap in overlaps:
            self.overlaps.discard(overlap)
        return self
    '''
    '''
    # Validators
    def verify_allowed_molecule_type(self):
        if not isinstance(self.molecule,self.allowed_molecule_types):
            raise utils.ValidateError('Molecule and site incompatible.')
        return

    def verify_allowed_to_bind(self):
        if not self.allowed_to_bind:
            raise utils.ValidateError('This site is not allowed to have a bond.')
        return
    '''
'''
class Bond(entity.Entity):
    sites = OneToManyAttribute(Site,related_name='bond')
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
    sites = ManyToManyAttribute(Site,related_name='overlaps')

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

'''
class MoleculeFactory(object):
    def __init__(self,m_type=None,s_types=None,m_attr=None,s_attr=None):
        if m_type is None:
            m_type = Molecule
        if s_types is None:
            s_types = [Site]
        
        self.m_type = m_type
        self.s_types = s_types
        
        assert m_attr is None or isinstance(m_attr,dict)
        assert s_attr is None or isinstance(s_attr,list)
        if s_attr is not None:
            assert(len(s_attr)==len(s_types))
            for x in s_attr:
                assert(isinstance(x,dict))

        self.m_attr = m_attr
        self.s_attr = s_attr

    def create(self,m_idx,s_idx=None):
        if self.s_types is None:
            assert s_idx is None
        else:
            assert len(s_idx) == len(self.s_types)
        
        m = self.m_type(m_idx)
        ss = []
        if s_idx is not None:
            ss = [self.s_types[i](s_idx[i]) for i in range(len(s_idx))]

        if self.m_attr is not None:
            for k,v in self.m_attr.items():
                setattr(m,k,v)
        if self.s_attr is not None:
            for i,s in enumerate(ss):
                for k,v in self.s_attr[i].items():
                    setattr(s,k,v)

        m.add_sites(*ss)
        return m,ss