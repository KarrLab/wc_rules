"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""
import math, itertools, functools, collections, operator, pprint
from dataclasses import dataclass, field
from typing import Tuple, Dict
from backports.cached_property import cached_property
from collections import defaultdict

@dataclass(order=True,frozen=True)
class Mapping:
    # Note: this is intended to replace BiMap
    #__slots__ = ['sources','targets',]
    sources: Tuple[str]
    targets: Tuple[str]

    @cached_property
    def _dict(self):
        assert len(self.sources) == len(set(self.sources)), f"Non-unique mappings found in zip({self.sources},{self.targets})"
        return dict(zip(self.sources,self.targets)) 

    @classmethod
    def create(cls,sources,targets=None):
        if targets is None:
            targets = sources
        assert len(sources)==len(targets), f"Could not create mapping between {sources} and {targets}"
        return cls(tuple(sources),tuple(targets))

    def reverse(self):
        return self.__class__.create(self.targets,self.sources)

    def get(self,value):
        idx = self.sources.index(value)
        return self.targets[idx]

    def restrict(self,sources):
        return self.__class__.create(sources,self*sources)

    def __mul__(self,other):
        if isinstance(other,Mapping):
            return other.__class__.create(other.sources,self*other.targets)
        if isinstance(other,dict):
            return dict(zip(other.keys(), self*list(other.values())))
        elif isinstance(other,(list,tuple,set)):
            return other.__class__([self.get(x) for x in other])
        return self.get(other)

    def transform(self,d):
        return {self._dict[k]:d[k] for k in d if k in self.sources}

    def sort(self,order=None):
        if order is None:
            order = sorted(self.sources)
        return self.__class__.create(order,self*order)

    def iter_items(self):
        # returns k,v pairs from sources and targets respectively
        for s,t in zip(self.sources,self.targets):
            yield (s,t)

    def duplicate(self,mapping):
        return self.__class__.create(mapping*self.sources,mapping*self.targets)

    def pprint(self):
        return 'Mapping\n' + '\n'.join([f'{x}->{y}' for x,y in zip(self.sources,self.targets)]) + '\n'

    def pprint2(self,sep=','):
        return f'(({sep.join(self.sources)})->({sep.join(self.targets)}))'      

# Should be downgraded and removed
@dataclass(unsafe_hash=True)
class BiMap:
    # create and copy_from class methods sort items before creation
    #__slots__ = '_dict sources targets'.split()
    _dict: dict = field(compare=False)
    sources: tuple = field(init=False)
    targets: tuple = field(init=False)
    
    def __post_init__(self):
        self.sources = tuple(self._dict.keys())
        self.targets = tuple(self._dict.values())
    
    @classmethod
    def create(cls,sources,targets=None):
        if targets is None:
            targets = sources
        return BiMap(dict(sorted(zip(sources,targets))))

    def reverse(self):
        return BiMap(dict(sorted(zip(self.targets,self.sources))))

    # overloaded dict behaviors
    def items(self):
        return self._dict.items()

    def get(self,elem):
        return self._dict.__getitem__(elem)

    def __str__(self,format='dict'):
        s =  ', '.join('{x}->{y}'.format(x=x,y=y) for x,y in self.items())
        return '{{{s}}}'.format(s=s)

    def __repr__(self):
        return str(self)
    
    # BiMap behaviors
    def __mul__(self,other):
        # other can be just a dict
        # self = {x:0,y:1,z:2}, other = {x:y,y:z,z:x}, out = {x:1,y:2,z:0}
        # out(_) = self(other(_))
        return BiMap({x:self.get(y) for x,y in other.items()})

    def __lt__(self,other):
        assert self.sources == other.sources
        return self.targets < other.targets

    def replace(self,item):
        if isinstance(item,(list,tuple,set)):
            return item.__class__(self.replace(x) for x in item)
        if isinstance(item,dict):
            return {self.replace(x):self.replace(y) for x,y in item.items()}
        if isinstance(item,BiMap):
            return BiMap(dict( sorted((self.replace(x),self.replace(y)) for x,y in item.items()) ))
        return self.get(item)

class DictLike(object):

    def __init__(self,iterable=[]):
        ''' Container of objects that enables referencing by id '''
        self._dict = {}
        for x in iterable:
            self.add(x)

    def get(self,key,value=None):
        # get ONLY works with id
        if key not in self._dict:
            return value
        return self._dict[key]

    def add(self,item):
        # add ONLY works with item, not id
        assert item.id not in self._dict,   f"Could not add item with id `{item.id}` as another item exists with the same id."
        self._dict[item.id] = item
        return self

    def remove(self,item):
        # remove ONLY works with item, not id
        self._dict.pop(item.id)
        return self

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict.values())

    def __contains__(self,item):
        return item in self._dict.values()

    def keys(self): return list(self._dict.keys())
    def values(self): return list(self._dict.values())
    def items(self): return list(self._dict.items())

    def __getitem__(self,key): return self._dict[key]

    def __eq__(self,other):
        return self._dict == other._dict

    def __add__(self,other):
        return self.__class__([*self.values(),*other.values()])

    def pop(self,idx):
        item = self._dict.pop(idx)
        return item


############ functional programming
def merge_lists(list_of_lists):
    return list(itertools.chain(*list_of_lists))

def merge_dicts(list_of_dicts):
    # ensure keys dont overlap
    return dict(collections.ChainMap(*list_of_dicts))

def merge_dicts_strictly(list_of_dicts):
    # build master list of keys
    outd, keys = dict(), set(merge_lists([d.keys() for d in list_of_dicts]))
    for key in keys:
        values = set([d.get(key,None) for d in list_of_dicts]) - set([None])
        assert len(values) == 1, f'Key {key} is mapped to multiple values {values} and cannot be merged.'
        outd[key] = values.pop()
    return outd

def is_one_to_one(_dict):
    assert None not in _dict.values()
    return len(set(_dict.values())) == len(_dict)


def no_overlaps(list_of_iters):
    joint_set = set.union(*[set(x) for x in list_of_iters])
    return len(joint_set) == len(merge_lists(list_of_iters))

def pipe_map(operations,inputs):
    if len(operations)==0:
        return inputs
    #item = list_of_operations.pop(0)
    return pipe_map(operations[1:],map(operations[0],inputs))

def listmap(op,inputs):
    return list(map(op,inputs))

def split_string(s,sep='\n'):
    return [y for y in [x.strip() for x in s.split(sep)] if len(y)>0]

def grouper(inputs,n):
    # assume len(input) is a multiple of n:
    # grouper(2,[1,2,3,4,5,6]) -> [[1,2],[3,4],[5,6]]
    return [inputs[n*i:n*i+n] for i in range(0,len(inputs)//n)]

def split_iter(inputs,n):
    outputs = [[] for i in range(n)]
    for i,x in zip(itertools.cycle(range(n)),inputs):
        outputs[i].append(x)
    return outputs

def remap_values(d,oldvalues,newvalue):
    for elem in d:
        if d[elem] in oldvalues:
            d[elem] = newvalue
    return d

###### Methods ######
def get_values(d,keys):
    return [d[k] for k in keys]
    
def iter_to_string(iterable):
    return '\n'.join([str(x) for x in list(iterable)])

def print_as_tuple(x):
    if isinstance(x,str):
        return x
    if isinstance(x,tuple):
        return '(' + ','.join((print_as_tuple(y) for y in x)) + ')'
    if isinstance(x,list):
        return '[' + ','.join((print_as_tuple(y) for y in x)) + ']'
    return str(x)

def listify(x):
    if isinstance(x,list): 
        return x
    return [x]

def tuplify(x):
    if isinstance(x,list):
        return tuple([tuplify(y) for y in x])
    return x

def subdict(d,keys,ignore=False):
    if ignore:
        keys = [x for x in keys if x in d] 
    return {k:d[k] for k in keys}

def triple_split(iter1,iter2):
    # L1, L2 are iters
    # returns (iter1-iter2), (iter1 & iter2), (iter2-iter1)
    s1, s2 = set(iter1), set(iter2)
    return [list(x) for x in [s1 - s2, s1 & s2, s2 - s1]]

def strgen(n,template='abcdefgh'):
    if n< len(template):
        return template[:n]

    # the +0.01 is to handle the case when n==1
    digits = math.ceil((math.log(n))/math.log(len(template)))
    enumerator = enumerate(itertools.product(template,repeat=digits))
    L = list(''.join(x) for i,x in enumerator if i<n)
    return L

def concat(LL):
    return [x for L in LL for x in L if x]

def printvars(vars,vals,sep=',',breakline=False):
    strs = ['{x}={y}'.format(x=x,y=y) for x,y in zip(vars,vals)]
    return sep.join(strs)

def invert_dict(_dict):
    out = collections.defaultdict(list)
    for k,v in _dict.items():
        out[v].append(k)
    return dict(out)

def verify_list(_list,_types):
    if not isinstance(_list,list):
        return isinstance(_list,_types)
    return all([verify_list(elem,_types) for elem in _list])

def tuplify_dict(_dict):
    return tuple(sorted(_dict.items()))

def all_unique(_list):
    return len(set(_list)) == len(_list)

def sort_by_value(_dict):
    values = collections.Counter(_dict.values()).keys()
    leaders = collections.defaultdict(list)
    for v in values:
        for k,x in _dict.items():
            if x==v:
                leaders[v].append(k)
    return list(leaders.values())

def ordered_unique(iterable):
    return {k:1 for k in iterable}.keys()

def index_dict(iterable):
    return dict(zip(iterable,range(len(iterable))))

def accumulate(iter_of_pairs,fn=lambda x:x):
    d = defaultdict(list)
    for x,y in iter_of_pairs:
        d[x].append(fn(y))
    return dict(d)

def rotate_until(dq,conditionfn):
    nrots = 0
    while not conditionfn(dq[0]):
        dq.rotate(-1)
        nrots += 1
        assert nrots < len(dq)
    return dq

def quoted(x):
    return f'\"{x}\"' if isinstance(x,str) else x

def unzip(zipped):
    return list(zip(*zipped))

class UniversalSet:

    def __contains__(self,x):
        return True

class ExclusionSet:

    def __init__(self,elems):
        self._exclude = set(elems)

    def __contains__(self,x):
        return x not in self._exclude

