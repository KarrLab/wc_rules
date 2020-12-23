"""
:Author: John Sekar <johnarul.se
kar@gmail.com>
:Date: 2018-04-20
:Copyright: 2017, Karr Lab
:License: MIT
"""
from obj_model import core
from . import base,entity,utils
from .attributes import *

class Molecule(entity.Entity):
    pass

class Site(entity.Entity):
    molecule = ManyToOneAttribute(Molecule,related_name='sites')
    bond = OneToOneAttribute('Site',related_name='bond')
    
    
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
        # returns a list with first element molecule and the rest sites
        return (m,) + tuple(ss)