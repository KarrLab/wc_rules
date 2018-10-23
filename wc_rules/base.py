""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
from . import graph_utils
from . import utils
from .attributes import *
import uuid
import random

# Seed for creating ids
# To modify this seed, load base module, then execute base.idgen.seed(<new_seed>)
idgen = random.Random()
idgen.seed(0)

###### Structures ######
class BaseClass(core.Model):
    """ Base class for bioschema objects.

    Attributes:
        id (:obj:`str`): unique id that can be used to pick object from a list

    Properties:
        label (:obj:`str`): name of the leaf class from which object is created
    """
    #id = StringAttribute(primary=True, unique=True)
    id = IdAttribute()
    attribute_properties = dict()

    class GraphMeta(graph_utils.GraphMeta):
        outward_edges = tuple()
        semantic = tuple()

    def __init__(self, *args, **kwargs):
        super(BaseClass, self).__init__(**kwargs)
        if 'id' not in kwargs.keys():
            if args:
                self.id = args[0]
            else:
            #self.id = str(uuid.UUID(int=idgen.getrandbits(128)))
                self.id = utils.generate_id()
        self.attribute_properties = self.make_attribute_properties_dict()

    def make_attribute_properties_dict(self):
        attrdict = dict()
        cls = self.__class__

        def populate_attribute(attrname, attr, check='related_class'):
            x = {'related': False, 'append': False, 'related_class': None}
            if check == 'related_class' and hasattr(attr, 'related_class'):
                x['related'] = True
                x['related_class'] = attr.related_class
                if isinstance(attr, (OneToManyAttribute, ManyToManyAttribute,)):
                    x['append'] = True
                x['related_attr'] = attr.related_name
            elif check == 'primary_class' and hasattr(attr, 'primary_class'):
                x['related'] = True
                x['related_class'] = attr.primary_class
                if isinstance(attr, (ManyToManyAttribute, ManyToOneAttribute,)):
                    x['append'] = True
                x['related_attr'] = attr.name
            return x

        for attrname, attr in cls.Meta.attributes.items():
            attrdict[attrname] = dict()
            attrdict[attrname].update(populate_attribute(attrname, attr, 'related_class'))
        for attrname, attr in cls.Meta.related_attributes.items():
            if attrname not in attrdict:
                attrdict[attrname] = dict()
            attrdict[attrname].update(populate_attribute(attrname, attr, 'primary_class'))
        return attrdict

    def get_related_attributes(self):
        attrdict = self.attribute_properties
        return [x for x in attrdict if attrdict[x]['related']]

    def get_scalar_attributes(self):
        attrdict = self.attribute_properties
        return [x for x in attrdict if not attrdict[x]['related']]

    def get_nonempty_scalar_attributes(self,ignore_id=True):
        attrs = self.get_scalar_attributes()
        if ignore_id:
            attrs = [x for x in attrs if x!='id']
        return [x for x in attrs if getattr(self,x,None) is not None]

    def get_nonempty_related_attributes(self):
        attrs = self.get_related_attributes()
        final_attrs = []
        for attr in attrs:
            if self.attribute_properties[attr]['append']:
                if getattr(self,attr,[])!=[]: final_attrs.append(attr)
            else:
                if getattr(self,attr,None) is not None: final_attrs.append(attr)
        return final_attrs

    def duplicate(self,id=None,preserve_id=False,attrlist=None):
        ''' duplicates node up to scalar attributes '''
        new_node = self.__class__()
        if attrlist is None:
            attrlist = self.get_nonempty_scalar_attributes()
        else:
            attrlist = set(self.get_nonempty_scalar_attributes()) - set(attrlist)
        for attr in attrlist:
            if attr=='id': continue
            setattr(new_node,attr,getattr(self,attr))
        if id:
            new_node.set_id(id)
        elif preserve_id:
            # use cautiously
            new_node.set_id(self.id)
        return new_node

    def duplicate_relations(self,target,nodemap,attrlist=None):
        ''' Duplicates self's relations, converts them using nodemap {id:new_node}, and applies to targetself.
        E.g. if old A1->X1, and nodemap { A1.id:A2, X1.id:X2 }
        A1.duplicate_relations(A2,nodemap) builds the new edge A2->X2
         '''
        if attrlist is None:
            attrlist = self.get_nonempty_related_attributes()
        else:
            attrlist = set(self.get_nonempty_related_attributes()) - set(attrlist)
        for attr in attrlist:
            old_relations = utils.listify(getattr(self,attr))
            converted_old_relations = [nodemap[x.id] for x in old_relations]
            new_relations = utils.listify(getattr(target,attr))
            to_add = set(converted_old_relations) - set(new_relations)
            if len(to_add) > 0:
                if self.attribute_properties[attr]['append']:
                    getattr(target,attr).extend(list(to_add))
                else:
                    setattr(target,attr,to_add.pop())
        return self

    def set_id(self, id):
        """ Sets id attribute.

        Args:
            id (:obj:`str`)

        Returns:
            self
        """
        self.id = id
        return self

    def get_id(self): return self.id

    @property
    def label(self):
        """ Name of the leaf class from which object is created.
        """
        return self.__class__.__name__

    ##### Graph Methods #####
    def get_graph(self, recurse=True, memo=None):
        return graph_utils.get_graph(self, recurse=recurse, memo=memo)

    @property
    def graph(self):
        return self.get_graph(recurse=True)
