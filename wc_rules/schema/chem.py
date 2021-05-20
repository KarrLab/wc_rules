"""
:Author: John Sekar <johnarul.se
kar@gmail.com>
:Date: 2018-04-20
:Copyright: 2017, Karr Lab
:License: MIT
"""

from . import base,entity
from .attributes import *

class Molecule(entity.Entity):
    pass

class Site(entity.Entity):
    molecule = ManyToOneAttribute(Molecule,related_name='sites')
    bond = OneToOneAttribute('Site',related_name='bond')


def bngize(mol,use_classnames=False):

    if not use_classnames:
        f = lambda x: x.id
    else:
        f = lambda x: x.__class__.__name__

    m = f(mol)
    s = ','.join([f(s) for s in mol.sites])
    return '{m}({s})'.format(m=m,s=s)


