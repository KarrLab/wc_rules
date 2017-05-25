"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

from attrdict import AttrDict
from wc_rules import exceptions
import obj_model.core


class Entity(obj_model.core.Model):
    """ Base class for model entities

    Attributes:
        to (:obj:`list` of :obj:`Entity`): list of outgoing entities
        from (:obj:`list` of :obj:`Entity`): list of incoming entities
    """
    to = obj_model.core.ManyToManyAttribute('Entity', related_name='from')
    _props = AttrDict()

    @property
    def label(self):
        """ Label of the object

        :getter: Get the name of type of the object
        :type: :obj:`str`
        """
        return self.__class__.__name__

    @property
    def id(self):
        """ Python id of the object

        :getter: Get the Python id of the object
        :type: :obj:`int`
        """
        return id(self)

    # Controls what types of entities can be added to this entity
    class EntitySignature(object):
        allowed_entity_types = tuple()
        min_allowed = dict()
        max_allowed = dict()

    # Controls what types of properties can be specified for this entity
    class PropertySignature(object):
        names = ('label', 'id',)
        allowed_types = {'label': str, 'id': int}
        settable = {'label': False, 'id': False}

    @classmethod
    def signature(cls):
        a = cls.EntitySignature.allowed_entity_types 
        min = cls.EntitySignature.min_allowed 
        max = cls.EntitySignature.max_allowed
        temp_dict1 = {'allowed': a, 'min': min, 'max': max}

        names, types = cls.PropertySignature.names, cls.PropertySignature.allowed_types
        str1 = 'EntitySignature'
        str2 = temp_dict1.__str__()
        str3 = 'PropertySignature'
        str4 = types.__str__()
        return '\n'.join([str1, str2, str3, str4])

    @classmethod
    def register_new_addable(cls, cls2, min=0, max=None):
        if cls2 not in cls.EntitySignature.allowed_entity_types:
            cls.EntitySignature.allowed_entity_types += (cls2,)
        cls.EntitySignature.min_allowed[cls2] = min
        cls.EntitySignature.max_allowed[cls2] = max

    @classmethod
    def register_new_property(cls, name, type_=bool, settable=True):
        cls.PropertySignature.names += (name,)
        cls.PropertySignature.allowed_types[name] = type_
        cls.PropertySignature.settable[name] = settable

    def __contains__(self, other):
        """ Determine if :obj:`self.to` contains :obj:`other`

        Args:
            other (:obj:`Entity`): another entity

        Returns:
            :obj:`bool`: if :obj:`other` is an element of obj:`self.to`
        """
        return other in self.to

    def append(self, other):
        """ Create a link from :obj:`self` to another entity :obj:`other`

        Args:
            other (:obj:`Entity`): another entity

        Returns:
            :obj:`Entity`: self
        """
        allowed_types = self.__class__.EntitySignature.allowed_entity_types
        if not isinstance(other, allowed_types):
            raise exceptions.Error('type error')

        curr_length = len(self.to.filter(label=other.label))
        max_length = self.EntitySignature.max_allowed[type(other)]
        if curr_length >= max_length:
            raise exceptions.Error('length error')
        self.to.append(other)
        return self

    def get_property(self, name):
        """ Get the value of the property with name :obj:`name`

        Args:
            name (:obj:`str`): property name 

        Returns:
            :obj:`object`: property value

        Raises:
            :obj:`exceptions.Error`: if :obj:`name` is not the name of a property
        """
        if name not in self.__class__.PropertySignature.names:
            raise exceptions.Error('name error')
        return self._props.__getattr__(name)

    def set_property(self, name, value):
        """ Set the value of the property with name :obj:`name`
        
        Args:
            name (:obj:`str`): property name 
            value (:obj:`object`): new property value

        Returns:
            :obj:`Entity`: self

        Raises:
            :obj:`exceptions.Error`: if :obj:`name` is not the name of a property
        """        
        if name not in self.__class__.PropertySignature.names:
            raise exceptions.Error('name error')
        if not self.__class__.PropertySignature.settable[name]:
            raise exceptions.Error('not settable')
        allowed_type = self.__class__.PropertySignature.allowed_types[name]
        if value is not None and not isinstance(value, allowed_type):
            raise exceptions.Error('type error')
        self._props.__setattr__(name, value)

        return self
