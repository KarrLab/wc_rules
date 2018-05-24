"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""
from wc_rules import utils
class Slicer(dict):
    def __init__(self,default=False):
        if not isinstance(default,bool):
            raise utils.SlicerError('`default` argument must be bool.')
        self.default = default

    def __getitem__(self,key):
        if key in self:
            return dict.__getitem__(self,key)
        return self.default

    def add_keys(self,keys):
        for key in keys:
            self[key] = not self.default
        return self

    def delete_keys(self,keys):
        for key in keys:
            self.pop(key)
        return self

    def update(self,dict_obj):
        not_default = not self.default
        keys = (key for key in dict_obj if dict_obj[key] is not_default)
        self.add_keys(keys)
        keys = (key for key in dict_obj if dict_obj[key] is self.default)
        keys1 = (key for key in keys if key in self)
        self.delete_keys(keys1)
        return self

    def union(self,other):
        if self.default != other.default:
            raise utils.SlicerError('Cannot merge positive and negative slicers.')
        keys = set(self.keys()) | set(other.keys())
        return Slicer(default=self.default).add_keys(keys)

    def intersection(self,other):
        if self.default != other.default:
            raise utils.SlicerError('Cannot intersect positive and negative slicers.')
        keys = set(self.keys()) & set(other.keys())
        return Slicer(default=self.default).add_keys(keys)

    def __and__(self,other):
        [x1,x2] = sorted([self,other],key=len)
        if self.default==other.default==False:
            return x1.intersection(x2)
        elif self.default==other.default==True:
            return x2.union(x1)
        elif self.default==False:
            keys = (key for key in self if other[key])
            return Slicer(default=False).add_keys(keys)
        return other & self

    def __or__(self,other):
        [x1,x2] = sorted([self,other],key=len)
        if self.default==other.default==False:
            return x2.union(x1)
        elif self.default==other.default==True:
            return x1.intersection(x2)
        elif self.default==True:
            keys = (key for key in self if not other[key])
            return Slicer(default=True).add_keys(keys)
        return other | self

    def __invert__(self):
        return Slicer(default= not self.default).add_keys(self.keys())

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

    def add_keys(self,keylist):
        return self.update(dict(zip(keylist,[not self.default]*len(keylist))))

    def __getitem__(self,key):
        if key not in self:
            return self.default
        return dict.__getitem__(self,key)

    # Methods available to combine indexers
    def union(self,other):
        ''' Merges keys of indexers as long as they all have the same default. '''
        if self.default != other.default:
            raise utils.IndexerError('Postive and negative indexers cannot be combined.')
        if len(self) >= len(other):
            x1 = self
            x2 = other
        else:
            x1 = other
            x2 = self
        keys = list(x1.keys()) + [k for k in x2.keys() if k not in x1.keys()]
        return BooleanIndexer(default=self.default).add_keys(keys)

    def intersection(self,other):
        ''' Returns common keys of indexers as long as they all have the same default. '''
        if self.default != other.default:
            raise utils.IndexerError('Postive and negative indexers cannot be combined.')
        if len(self) <= len(other):
            x1 = self
            x2 = other
        else:
            x1 = other
            x2 = self
        keys = [key for key in x1 if key in x2]
        return BooleanIndexer(default=self.default).add_keys(keys)

    def __and__(self,other):
        ''' New indexer that returns True if both indexers return True. Overloads operator `&`. '''
        if self.default==other.default==False:
            # Case 1 both are positive indexers (default:False)
            return self.intersection(other)
        if self.default==other.default==True:
            # Case 2 both are negative indexers (default:True)
            # By DeMorgan's law A' & B' = (A|B)'
            return self.union(other)
        if self.default==False and other.default==True:
            # Case 3 self is positive indexer, but other is negative
            # Include keys from self as long as other returns True
            keys = (key for key in self if other[key])
            return BooleanIndexer(default=False).add_keys(keys)
        if self.default==True and other.default==False:
            # Case 4, same as case 3, but interchanged
            return other & self
        return

    def __or__(self,other):
        ''' New indexer that returns True if at least one indexer returns True. Overloads operator `|`. '''
        if self.default==other.default==False:
            # Case 1 both are positive indexers (default:False)
            return self.union(other)
        if self.default==other.default==True:
            # Case 2 both are negative indexers (default:True)
            # By DeMorgan's law A' | B' = (A&B)'
            return self.intersection(other)
        if self.default==True and other.default==False:
            # Case 3 self is negative indexer, but other is positive
            # Include keys from self as long as other returns False
            keys = (key for key in self if not other[key])
            return BooleanIndexer(default=True).add_keys(keys)
        if self.default==True and other.default==False:
            # Case 4, same as case 3, but interchanged
            return other | self

    def __invert__(self):
        ''' Inverts truth values of a boolean indexer. Overloads operator `~`. '''
        return BooleanIndexer(default= not self.default).add_keys(self.keys())
