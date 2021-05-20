"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from . import base
from .actions import ActionMixin

class Entity(base.BaseClass,ActionMixin):

    
    @classmethod
    def get_classnames(cls):
        x,names = cls, []
        while x.__name__ is not 'Entity':
        	names.append(x.__name__)
        	x = x.__bases__[0]
        return names

    
    def has_label(self,label):
    	return label in self.__class__.get_classnames()

    setattr(has_label,'_is_computation',True)

    @classmethod
    def default_name(cls):
        print(cls.__bases__)
        return cls.__class__.__name__.lower()


    
