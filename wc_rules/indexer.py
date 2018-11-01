"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""
from . import utils
import inspect
import pprint

class DictLike(object):
    def __init__(self,iterable=None):
        ''' Container of objects that enables referencing by id '''
        if iterable is not None:
            self._dict = dict(iterable)
        else:
            self._dict = dict()

    def get(self,key):
        return self._dict[key]

    def add(self,item):
        self._dict[item.id] = item
        return self

    def remove(self,item):
        self._dict.pop(item.id)
        return self

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict.values())

    def __contains__(self,item):
        return item.id in self._dict and item is self._dict[item.id]


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
        psl(A) | nsl(B) = nsl(B - intersection(A,B))
        nsl(A) | psl(B) = nsl(A - intersection(A,B))
        nsl(A) | nsl(B) = nsl(intersection(A,B))
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

class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def __contains__(self,other):
        if isinstance(other,dict):
            return all(item in self.items() for item in other.items())
        return dict.__contains__(self,other)

class Index_By_ID(dict):
    '''A dict that looks like a list, but enables recovering by ID'''
    def append(self,obj1):
        self[obj1.id] = obj1
        return self

    def remove(self,obj1):
        del self[obj1.id]

    def retrieve(self,idx):
        return self[idx]

    def __contains__(self,obj1):
        return obj1.id in self.keys()

class DictSet(object):
    ''' A container that is primarily a set, but also indexes the elements using a key function (default keyfunc is getting the object's id).'''

    def __init__(self,iterable=None,keyfunc=None):
        self._set = set()
        self._dict = dict()
        if keyfunc is None:
            keyfunc = lambda x: x.id
        self._keyfunc = keyfunc

        if iterable:
            elems = set(iterable)
            self._set.update(elems)
            for elem in elems:
                self._dict[self._keyfunc(elem)] = elem

    def add(self,elem):
        self._set.add(elem)
        self._dict[self._keyfunc(elem)] = elem
        return self

    def remove(self,elem):
        self._set.remove(elem)
        self._dict.pop(self._keyfunc(elem))
        return self

    def __contains__(self,other):
        # set behavior
        return other in self._set

    def __getitem__(self,key):
        # dict behavior
        return self._dict[key]

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return iter(self._set)

    def __str__(self):
        return str(sorted(self._set,key=self._keyfunc))
        #return pprint.pformat(sorted(self._set,key=self._keyfunc))


class Indexer(dict):
    '''
    A hashmap between keys (literals or named tuples) and arbitary values of the same type
    (set by the primitive_type class attribute).

    If I is an indexer object,
    I[key] - returns the value mapped to key
    I[slice] - returns an indexer which is a subset of the previous indexer, with keys from slice.

    In addition to dict-like behavior, Indexer maintains a value cache, which supports
    reverse lookup of keys from values using the `==` and `!=` operators

    I == value          returns a slice of keys such that I[key]==value
    I == list_of_values returns a slice of keys such that I[key] in list_of_values
    I1 == I2            returns a slice of keys with equal values in I1 and I2
    I != x              returns ~(I==x) where x is a value, list of values or indexer.

    Alternatively, one can use the slice method
    I.slice(value)          same as I==value
    I.slice(list_of_values) same as I==list_of_values
    I.slice(function)       returns a slice of keys whose values evaluate to True under function.

    Slicing and subsetting can be done simultaneously, e.g., I[I==value].

    Also, Indexer maintains a last_updated list of keys, which is propagated by default when a subset is created.
    '''
    primitive_type = None

    def __init__(self):
        self.value_cache = {}
        self.last_updated = Slicer(default=False)

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

    def update_last_updated(self,keylist):
        if isinstance(keylist,list):
            self.last_updated.add_keys(keylist)
        else:
            self.last_updated.add_keys(list(keylist))
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
        if propagate==True:
            I.update_last_updated(self.last_updated.keys())
        return I

    def update_key_value(self,key,value):
        if self.value_is_compatible(value):
            if key in self: self.delete_key_from_value_cache(key)
            dict.__setitem__(self,key,value)
            self.add_key_to_value_cache(key,value)
        return self

    def remove_key(self,key):
        self.delete_key_from_value_cache(key)
        self.pop(key)
        return self

    def update(self,dict_obj):
        keys = (key for key in dict_obj if (key in self and self[key]!=dict_obj[key]) or key not in self)
        for key in keys:
            self.update_key_value(key, dict_obj[key])
            self.update_last_updated(key)
        return self

    def remove(self,keylist):
        keys = (key for key in keylist if key in self)
        for key in keys:
            self.remove_key(key)
            self.update_last_updated(key)
        return self

    def flush(self):
        self.last_updated = Slicer(default=False)
        return self

    def __eq__(self,other):
        if isinstance(other,Indexer):
            S = Slicer(default=False)
            for val in self.value_cache:
                if val in other.value_cache:
                    x = self.slice([val]) & other.slice([val])
                    S = S | x
            return S
        if isinstance(other,dict):
            keys = (key for key in self if other in key)
            return Slicer(default=False).add_keys(keys)
        if isinstance(other,self.primitive_type):
            return self.slice([other])
        if isinstance(other,list):
            return self.slice(other)
        raise utils.IndexerError('To use __eq__ or __ne__, either compare two Indexers, or an indexer and a compatible value, or an indexer and a list of compatible values.')

    def __ne__(self,other):
        return ~self.__eq__(other)

class BooleanIndexer(Indexer):
    primitive_type = bool

class NumericIndexer(Indexer):
    '''
    In additon to operators `==` and `!=`, NumericIndexer also supports `>`,`>=`, `<` and `<=`

    I1 > I2            returns a slice for all keys in I1 whose values in I1 are greater than their values in I2
    I > value          returns a slice for all keys in I mapped to values greater than `value`
    I > list_of_values is not supported
    '''
    primitive_type = (int,float,)

    def __lt__(self,other):
        if isinstance(other,Indexer):
            keys =(key for key in self if key in other and self[key] < other[key])
            return Slicer(default=False).add_keys(list(keys))
        if isinstance(other,self.primitive_type):
            return self.slice(lambda x: x < other)
        raise utils.IndexerError('To use __le__, __lt__, __ge__,__gt__, either compare two Indexers, or an indexer and a compatible value.')

    def __gt__(self,other):
        if isinstance(other,Indexer):
            keys =(key for key in self if key in other and self[key] > other[key])
            return Slicer(default=False).add_keys(list(keys))
        if isinstance(other,self.primitive_type):
            return self.slice(lambda x: x > other)
        raise utils.IndexerError('To use __le__, __lt__, __ge__,__gt__, either compare two Indexers, or an indexer and a compatible value.')

    def __le__(self,other):
        x1 = self < other
        x2 = self == other
        return x1|x2

    def __ge__(self,other):
        x1 = self > other
        x2 = self == other
        return x1|x2

class StringIndexer(Indexer):
    primitive_type = str
