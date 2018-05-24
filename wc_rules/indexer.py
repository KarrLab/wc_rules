"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""

class Indexer(dict):
    primitive_type = None

    def __init__(self,default=None):
        self._values = {}
        self.last_updated = set()
        self.default = default

    # Internal methods
    def key_exists(self,key):
        return key in self

    def value_exists(self,value):
        return value in self._values

    def value_is_compatible(self,value):
        if self.primitive_type is not None:
            if not isinstance(value,self.primitive_type):
                raise utils.IndexerError('Value is not compatible with indexer type')
        return True

    def value_is_default(self,value):
        if self.default is not None:
            return self.default==value
        return False

    def delete_key(self,key):
        value = self.pop(key)
        self._values[value].pop(key)
        if len(self._values[value])==0:
            self._values.pop(value)
        return self

    def create_new_key_value(self,key,value):
        dict.__setitem__(self,key,value)
        if not self.value_exists(value):
            self._values[value] = dict()
        self._values[value][key] = True
        return self

    def update_key_value(self,key,value):
        self.value_is_compatible(value)
        if self.key_exists(key) and self[key] != value:
            self.delete_key(key)
        if not self.value_is_default(value):
            self.create_new_key_value(key,value)
        return self

    def update_last_updated(self,key):
        self.last_updated.add(key)
        return self

    # Methods available to paired queryobjects
    def update(self,dict_obj):
        for key,val in dict_obj.items():
            self.update_key_value(key,val)
            self.update_last_updated(key)
        return self

    def remove(self,keylist):
        for key in keylist:
            self.delete_key(key)
            self.update_last_updated(key)
        return self

    def flush(self):
        self.last_updated.clear()
        return self

class BooleanIndexer(Indexer):
    primitive_type = bool

    def __init__(self,default=False):
        super(BooleanIndexer,self).__init__()
        self.default = default

    def __getitem__(self,key):
        if isinstance(key,BooleanIndexer):
            I = key
            keys = (key for key in self if I[key])
            return BooleanIndexer(default=self.default).update({key:self[key] for key in keys})
        if isinstance(key,list):
            L = key
            keys = (key for key in self if key in L)
            return BooleanIndexer(default=self.default).update({key:self[key] for key in keys})
        if key not in self:
            return self.default
        return dict.__getitem__(self,key)

    # Methods available to combine indexers
    def __and__(self,other):
        ''' Filters common keys of two boolean indexers. Overloads operator `&`. '''
        if len(self) <= len(other):
            x1,x2 = self,other
        else:
            x1,x2 = other,self
        gen = (key for key in x1 if x1[key]==True and key in x2 and x2[key]==True)
        return BooleanIndexer().update({key:x1[key] for key in gen})

    def __or__(self,other):
        ''' Combines common keys of two boolean indexers. Overloads operator `|`. '''
        keys = set(list(self) + list(other))
        valfunc = lambda x: self.get(x,False) or other.get(x,False)
        return BooleanIndexer().update({key:valfunc(key) for key in keys})

    def __invert__(self):
        ''' Inverts truth values of a boolean indexer. Overloads operator `~`. '''
        return BooleanIndexer(default= not self.default).update({key:not self[key] for key in self})
