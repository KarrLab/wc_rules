"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""
from wc_rules import utils
import inspect
class Slicer(dict):
    ''' A hashmap between keys (literals or namedtuples) and Boolean values.
    Slicers are dict-like and always return True or False when queried with [key].
    Slicers may be positive slicers (psl's) or negative slicers (nsl's).
    Given set A,
        psl(A) represents set A
        nsl(A) represents complement(A)
    The operator `~` inverts positive and negative slicers.
        ~psl(A) = nsl(A)
        ~nsl(A) = psl(B)
    The operator `&` performs a set intersection according to deMorgan's laws.
        psl(A) & psl(B) = psl(intersection(A,B))
        psl(A) & nsl(B) = psl(A - intersection(A,B))
        nsl(A) & psl(B) = psl(B - intersection(A,B))
        nsl(A) & nsl(B) = nsl(union(A,B))
    The operator `|` performs a set union according to deMorgan's laws.
        psl(A) | psl(B) = psl(union(A,B))
        psl(A) | nsl(B) = complement(B - intersection(A,B))
        nsl(A) | psl(B) = complement(A - intersection(A,B))
        nsl(A) | nsl(B) = complement(intersection(A,B))
    '''
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

    def __init__(self):
        self.value_cache = {}
        self.last_updated = set()

    def __getitem__(self,key):
        if isinstance(key,Slicer):
            return self.subset(key)
        return dict.__getitem__(self,key)

    # Internal methods
    def value_is_compatible(self,value):
        if self.primitive_type is not None:
            if not isinstance(value,self.primitive_type):
                raise utils.IndexerError('Value is not compatible with indexer type')
        return True

    def delete_key_from_value_cache(self,key):
        value = self[key]
        self.value_cache[value].pop(key)
        if len(self.value_cache[value])==0:
            self.value_cache.pop(value)
        return self

    def add_key_to_value_cache(self,key,value):
        if value not in self.value_cache:
            self.value_cache[value] = Slicer(default=False)
        self.value_cache[value].add_keys([key])
        return self

    def update_last_updated(self,key):
        self.last_updated.add(key)
        return self

    # Methods available externally
    def slice(self,value_list=None):
        S = Slicer(default=False)
        if value_list is None:
            S.add_keys(k for k in self)
            return S
        if inspect.isfunction(value_list):
            f = value_list
            value_list = (value for value in self.value_cache if f(value))
        for value in value_list:
            S = S | self.value_cache[value]
        return S

    def subset(self,keylist,propagate=True):
        cls = type(self)
        I = cls()
        if isinstance(keylist,list):
            keys = (key for key in self if key in keylist)
        if isinstance(keylist,Slicer):
            keys = (key for key in self if keylist[key])
        for key in keys:
            I.update_key_value(key,self[key])
            if propagate==True and key in self.last_updated:
                I.update_last_updated(key)
        return I

    def update_key_value(self,key,value):
        if key in self and self[key]==value:
            return self
        if self.value_is_compatible(value):
            if key in self: self.delete_key_from_value_cache(key)
            dict.__setitem__(self,key,value)
            self.add_key_to_value_cache(key,value)
        return self

    def remove_key(self,key):
        if key not in self:
            return self
        self.delete_key_from_value_cache(key)
        self.pop(key)
        return self

    def update(self,dict_obj):
        for key in dict_obj:
            self.update_key_value(key, dict_obj[key])
            self.update_last_updated(key)
        return self

    def remove(self,keylist):
        for key in keylist:
            self.remove_key(key)
            self.update_last_updated(key)
        return self

    def flush(self):
        self.last_updated.clear()
        return self

    def __eq__(self,other):
        if isinstance(other,Indexer):
            values = (value for value in self.value_cache if value in other.value_cache)
            S = Slicer(default=False)
            for value in values:
                slice = self.slice([value]) & other.slice([value])
                S = S | slice
            return S
        if isinstance(other,self.primitive_type):
            return self.slice([other])
        if isinstance(other,list):
            S = Slicer(default=False)
            for value in other:
                slice = self.slice([value])
                S = S | slice
        # test against a list of values
        raise utils.IndexerError('To use __eq__, either compare two Indexers, or an indexer and a compatible value, or an indexer and a list of compatible values.')

class BooleanIndexer(Indexer):
    primitive_type = bool

class NumericIndexer(Indexer):
    primitive_type = (int,float,)

class StringIndexer(Indexer):
    primitive_type = str
