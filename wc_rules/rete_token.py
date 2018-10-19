from .utils import generate_id, iter_to_string

class Token(object):
    def __init__(self,contents=None):
        self._dict = dict()
        if contents:
            for key,value in contents.items():
                self.__setitem__(key,value)

    def __setitem__(self,key,value):
        self._dict[key] = value
        return self

    def __getitem__(self,key):
        return self._dict[key]

    def __str__(self):
        type1 =  self.get_type()
        return type1 + ':' + str(self._dict)
        #return " ".join(['token',type1+":"+str(self._dict)])

    def __contains__(self,key):
        return key in self._dict
    '''
    def update(self,tok):
        common_keys = set(tok.keys()) & set(self.keys())
        different_keys = set(tok.keys()) - common_keys
        for key in common_keys:
            assert(self[key]==tok[key])
        for key in different_keys:
            self.__setitem__(key,tok[key])
        return self
    '''

    def merge(self,token):
        common_keys = set(self.keys()) & set(token.keys())
        new_keys = set(token.keys()) - common_keys
        for key in common_keys:
            if self[key] != token[key]:
                return None
        for key in new_keys:
            if token[key] in self.values():
                return None
        newtoken = new_token(self)
        for key in new_keys:
            newtoken[key] = token[key]
        return newtoken

    def items(self): return self._dict.items()
    def keys(self): return self._dict.keys()
    def values(self): return self._dict.values()

    def subset(self,keys):
        return {k:self[k] for k in keys if k in self._dict}

    def get_subtoken(self,keys):
        return self.__class__(self.subset(keys))

    def get_type(self): return None

class AddToken(Token):
    def get_type(self): return 'add'

class RemoveToken(Token):
    def get_type(self): return 'remove'

def new_token(token,invert=False,keymap=None,subsetkeys=None):
    d = token._dict
    if subsetkeys is None:
        subsetkeys = token.keys()
    if keymap:
        d = {keymap[x]:y for x,y in token.items() if x in subsetkeys}
    _class = None
    if not invert:
        _class = token.__class__
    else:
        inv = {AddToken:RemoveToken,RemoveToken:AddToken}
        _class = inv[token.__class__]
    return _class(d)

class TokenRegister(object):
    def __init__(self):
        self._dict = dict()
        self._set = set()

    def __str__(self):
        return iter_to_string(self._set)

    def __len__(self):
        return len(self._set)

    def register(self,key,value,token):
        t = tuple([key,value])
        if t not in self._dict:
            self._dict[t] = set()
        self._dict[t].add(token)
        return self

    def deregister(self,key,value,token):
        t = tuple([key,value])
        if t in self._dict:
            self._dict[t].remove(token)
        if len(self._dict[t])==0:
            del self._dict[t]
        return self

    def add_token(self,token):
        for key,value in token.items():
            self.register(key,value,token)
        self._set.add(token)
        return self

    def remove_token(self,token):
        if token in self._set:
            for (key,value) in token.items():
                self.deregister(key,value,token)
            self._set.remove(token)
        return self

    def getkv(self,key,value):
        t = tuple([key,value])
        if t in self._dict:
            return self._dict[tuple([key,value])]
        return set()

    def filter(self,token):
        return set.intersection(*(self.getkv(key,value) for key, value in token.items()))

    def get(self,token):
        f = self.filter(token)
        assert 0 <= len(f) <=1
        if len(f)==1:
            return f.pop()
        return None

def token_add_node(node):
    attrlist = node.get_nonempty_scalar_attributes(ignore_id=True)
    return AddToken({'node':node,'modified_attrs':tuple(attrlist)})

def token_edit_attrs(node,attrlist):
    attrtuples = [(attr,getattr(node,attr)) for attr in attrlist]
    return AddToken({'node':node,'modified_attrs':tuple(attrlist)})

def token_remove_node(node):
    return RemoveToken({'node':node})

def flip_edge_correctly(node1,attr1,attr2,node2):
    as_is = True
    if attr1 > attr2 :
        as_is = False
    if not as_is:
        return node2,attr2,attr1,node1
    # TODO: Need to handle symmetric edges
    return node1,attr1,attr2,node2

def token_add_edge(node1,attr1,attr2,node2):
    node1,attr1,attr2,node2 = flip_edge_correctly(node1,attr1,attr2,node2)
    return AddToken({'node1':node1,'attr1':attr1,'attr2':attr2,'node2':node2})

def token_remove_edge(node1,attr1,attr2,node2):
    node1,attr1,attr2,node2 = flip_edge_correctly(node1,attr1,attr2,node2)
    return RemoveToken({'node1':node1,'attr1':attr1,'attr2':attr2,'node2':node2})
