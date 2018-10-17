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
        return " ".join(['token',str(self._dict)])

    def update(self,tok):
        common_keys = set(tok.keys()) & set(self.keys())
        different_keys = set(tok.keys()) - common_keys
        for key in common_keys:
            assert(self[key]==tok[key])
        for key in different_keys:
            self.__setitem__(key,tok[key])
        return self

    def items(self): return self._dict.items()
    def keys(self): return self._dict.keys()

    def subset(self,keys):
        return {k:self[k] for k in self._dict}

    def get_subtoken(self,keys):
        return self.__class__(self.subset(keys))


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
    if not invert:
        return token.__class__(d)
    inv = {AddToken:RemoveToken,RemoveToken:AddToken}
    return inv[token.__class__](d)

class TokenRegister(object):
    def __init__(self):
        self._dict = dict()
        self._set = set()

    def __str__(self):
        return iter_to_string(self._set)

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
    attrs = node.get_nonempty_scalar_attributes(ignore_id=True)
    return AddToken({'node':node,'modified_attrs':tuple(attrs)})

def token_edit_attrs(node,attrlist):
    return AddToken({'node':node,'modified_attrs':tuple(attrlist)})

def token_remove_node(node):
    return RemoveToken({'node':node})

def token_add_edge(node1,attr1,attr2,node2):
    return AddToken({'edge':(node1,attr1,attr2,node2)})

def token_remove_edge(node1,attr1,attr2,node2):
    return RemoveToken({'edge':(node1,attr1,attr2,node2)})
