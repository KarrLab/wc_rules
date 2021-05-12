"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""
import math, itertools, functools, collections, operator, pprint
from dataclasses import dataclass, field

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

    def get(self,key,value):
        if key not in self._dict:
            return value
        return self._dict[key]

    def add(self,item):
        if item.id in self._dict:
            assert self._dict[item.id] == item, 'Item {0} could not be added.'.format(item)
        else:
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
        return item in self._dict.values()

    def keys(self): return list(self._dict.keys())
    def values(self): return list(self._dict.values())
    def items(self): return list(self._dict.items())

    def __getitem__(self,key): return self._dict[key]

    def __str__(self):
        return pprint.pformat(self._dict)

    def __eq__(self,other):
        return self._dict == other._dict

    def __add__(self,other):
        return self.__class__([*self.values(),*other.values()])


############ functional programming
def merge_lists(list_of_lists):
    return list(itertools.chain(*list_of_lists))

def merge_dicts(list_of_dicts):
    # ensure keys dont overlap
    return dict(collections.ChainMap(*list_of_dicts))

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

def grouper(n,inputs):
    # assume len(input) is a multiple of n:
    # grouper(2,[1,2,3,4,5,6]) -> [[1,2],[3,4],[5,6]]
    return [inputs[n*i:n*i+n] for i in range(0,len(inputs)//n)]


###### Methods ######
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

def subdict(d,keys):
    return {k:d[k] for k in keys}

def strgen(n,template='abcdefgh'):
    # the +0.01 is to handle the case when n==0
    digits = math.ceil((math.log(n) + 0.01)/math.log(len(template)))
    enumerator = enumerate(itertools.product(template,repeat=digits))
    return list(''.join(x) for i,x in enumerator if i<n)

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

##### Validating data structures
