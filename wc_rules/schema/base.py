""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_tables import core
from ..utils.random import generate_id
from .attributes import *
from .actions import ActionMixin

from collections import deque

class BaseClass(core.Model,ActionMixin):
    ''' Base class for building objects '''
    id = IdAttribute()

    def __init__(self, *args, **kwargs):
        super(BaseClass, self).__init__(**kwargs)
        if 'id' not in kwargs.keys():
            if args:
                self.id = args[0]
            else:
                self.id = generate_id()
        self.attach_actions()

    @classmethod
    def resolve_classes(cls):
        _class = cls
        classes = list(reversed(_class.__mro__[:_class.__mro__.index(BaseClass)]))
        return classes

    def get_literal_attrdict(self,ignore_id=True,ignore_None=True):
        return {x:self.get(x) for x in self.get_literal_attributes(ignore_id=ignore_id,ignore_None=ignore_None)}

    def get_related_attrdict(self,ignore_None=True,use_id_for_related=False):
        d = {x:self.get(x) for x in self.get_related_attributes(ignore_None)}
        def convert_to_ids(v):
            if isinstance(v,list):
                return [x.id for x in v]
            elif v is not None:
                return v.id
            else:
                return v
        if use_id_for_related:
            d = {k:convert_to_ids(v) for k,v in d.items()}
        return d

    def get_attrdict(self,ignore_id=False,ignore_None=True,use_id_for_related=False):
        d1 = self.get_literal_attrdict(ignore_id=ignore_id,ignore_None=ignore_None)
        d2 = self.get_related_attrdict(ignore_None=ignore_None,use_id_for_related=use_id_for_related)
        return {**d1,**d2}
    
    def get_literal_attributes(self,ignore_id=False,ignore_None=False):
        # get_literal_attrs() is deterministic?
        # attrs are sorted?
        L = list(self.get_literal_attrs().keys())
        if ignore_id:
            L.remove('id')
        if ignore_None:
            L = [x for x in L if self.get(x) is not None]
        return L

    def get_related_attributes(self,ignore_None=False):
        # get_related_attrs() is deterministic?
        # attrs are sorted?
        L = list(self.get_related_attrs().keys())
        if ignore_None:
            L = [x for x in L if self.get(x) not in [[],None]]
        return L

    def get_related_name(self,attr):
        return self.__class__.Meta.local_attributes[attr].related_name

    def get_related_class(self,attr):
        return self.__class__.Meta.local_attributes[attr].related_class

    def get(self,attr,aslist=False):
        x = getattr(self,attr)
        if aslist and self.__class__.Meta.local_attributes[attr].is_related and not self.__class__.Meta.local_attributes[attr].is_related_to_many:
            if x is None:
                x = []
            else:
                x = [x]
        return x

    def listget(self,attr):
        return self.get(attr,aslist=True)
        
    def listget_all_related(self):
        x = set()
        for attr in self.get_related_attributes(ignore_None=True):
            x.update(self.listget(attr))
        return list(x)

    def degree(self):
        return len(list(self.iter_edges()))

    def iter_edges(self):
        for attr in self.get_related_attributes(ignore_None=True):
            for node in self.listget(attr):
                yield (attr,node)

    def iter_literal_attrs(self,ignore_id=True,ignore_None=True):
        for attr in self.get_literal_attributes(ignore_id=ignore_id,ignore_None=ignore_None):
            yield (attr,self.get(attr))
        
    def get_edge_tuples(self):
        # returns list of tuples (attr,related_attr,x)
        attrs = self.get_related_attributes(ignore_None=True)
        related = {a:self.get_related_name(a) for a in attrs}
        lists = [self.listget(a) for a in attrs]
        return [ tuple(sorted([(self.id,a), (x.id,related[a])])) for a,y in zip(attrs,lists) for x in y ]

    def duplicate(self,id=None,preserve_id=False):
        ''' duplicates node up to literal attributes '''
        attrdict = self.get_literal_attrdict(ignore_id=True,ignore_None=True)
        new_node = self.__class__(**attrdict)
        if id:
            new_node.id = id
        elif preserve_id:
            # use cautiously
            new_node.id = self.id
        return new_node

    def duplicate_relations(self,target,nodemap,attrlist=None):
        ''' Duplicates self's relations, converts them using nodemap {id:new_node}, and applies to targetself.
        E.g. if old A1->X1, and nodemap { A1.id:A2, X1.id:X2 }
        A1.duplicate_relations(A2,nodemap) builds the new edge A2->X2
         '''
        if attrlist is None:
            attrlist = self.get_related_attributes(ignore_None=True)
        else:
            attrlist = set(self.get_related_attributes(ignore_None=True)) - set(attrlist)
        for attr in attrlist:
            old_relations = self.listget(attr)
            converted_old_relations = [nodemap[x.id] for x in old_relations]
            new_relations = target.listget(attr)
            to_add = set(converted_old_relations) - set(new_relations)
            if len(to_add) > 0:
                if self.__class__.Meta.local_attributes[attr].is_related_to_many:
                    getattr(target,attr).extend(list(to_add))
                else:
                    setattr(target,attr,to_add.pop())
        return self

    @property
    def label(self):
        """ Name of the leaf class from which object is created.
        """
        return self.__class__.__name__

    def get_connected(self):
        nodes, examine_stack = [], deque([self])
        while examine_stack:
            node = examine_stack.popleft()
            if node not in nodes:
                nodes.append(node)
                examine_stack.extend(node.listget_all_related())
        return list(nodes)

    ################ this section is for safely doing actions during simulation
    def safely_set_attr(self,attr,value):
        # enforces class,min,max
        self.__class__.Meta.attributes[attr].check_value(value)
        setattr(self,attr,value)
        return self

    def safely_add_edge(self,attr,target):
        #y = self.__class__.Meta.attributes[attr]
        x = self.__class__.Meta.local_attributes[attr]
        err = 'Cannot add an edge to `{target.__class__.__name__}` instance using attribute `{attr}`.'
        assert isinstance(target, self.get_related_class(attr)), err.format(target=target,attr=attr)
        if x.is_primary:
            y = self.__class__.Meta.attributes[attr]
            min_related, max_related = y.min_related, y.max_related
            min_related_rev, max_related_rev = y.min_related_rev,y.max_related_rev
        else:
            y = target.__class__.Meta.attributes[self.get_related_name(attr)]
            min_related, max_related = y.min_related_rev,y.max_related_rev
            min_related_rev, max_related_rev = y.min_related, y.max_related
        err = 'Cannot add another edge to `{target.__class__.__name__}` instance using attribute `{attr}`.'
        assert len(self.listget(attr)) < max_related, err.format(target=target,attr=attr)
        attr2 = self.get_related_name(attr)
        assert len(target.listget(attr2)) < max_related_rev, err.format(target=self,attr=attr2)
        err = '`{target.__class__.__name__}` instance already found on attribute `{attr}`. Cannot add again.'
        assert target not in self.listget(attr), err.format(target=target,attr=attr)

        if x.is_related_to_many:
            a = getattr(self,attr)
            a.add(target)
        else:
            setattr(self,attr,target)
        return self

    def safely_remove_edge(self,attr,target):
        err = "`{target.__class__.__name__}` instance not found on attribute `{attr}`."
        assert target in self.listget(attr), err.format(target=target,attr=attr)
        if self.__class__.Meta.local_attributes[attr].is_related_to_many:
            a = getattr(self,attr)
            a.remove(target)
        else:
            setattr(self,attr,None)
        return self

    def __repr__(self):
        return 'Object of {0} with id \'{1}\''.format(self.__class__,self.id)


    def pprint(self):
        s = [f'<{self.__class__.__name__}: {self.id}>']
        for a,v in self.iter_literal_attrs():
            s.append(f'   {a}={v}')
        for a,n in self.iter_edges():
            s.append(f"   {a}--><{n.__class__.__name__}: {n.id}>")
        return '\n'.join(s)


    
        