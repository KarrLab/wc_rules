from .utils import generate_id, iter_to_string

class Token(object):
    def __init__(self,contents=None):
        self.id = generate_id()
        self._dict = dict()
        if contents:
            for key,value in contents.items():
                self.__setitem__(key,value)

    def __setitem__(self,key,value):
        self._dict[key] = value
        if hasattr(value,'_tokens'):
            value._tokens.add(self)
        return self

    def __getitem__(self,key):
        return self._dict[key]

    def __str__(self):
        return " ".join(['token',self.id,str(self._dict)])

    def update(self,tok):
        common_keys = set(tok.keys()) & set(self.keys())
        different_keys = set(tok.keys()) - common_keys
        for key in common_keys:
            assert(self[key]==tok[key])
        for key in different_keys:
            self.__setitem__(key,tok[key])
        return self

    def subset(self,keys):
        return { k:self[k] for k in keys }

    def prep_safe_delete(self):
        for value in self._dict.values():
            if hasattr(value,'_tokens'):
                value._tokens.remove(self)
        return self

    def items(self): return self._dict.items()
    def keys(self): return self._dict.keys()

    def modify_with_keymap(self,keymap):
        keys = list(self.keys())
        for key in keys:
            self[keymap[key]] = self[key]
            self._dict.pop(key)
        return self

    def duplicate_with_keymap(self,keymap=None):
        if keymap is None:
            return Token(self)
        t = Token()
        for key in self.keys():
            t[keymap[key]] = self[key]
        return t

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

    def get(self,key,value):
        t = tuple([key,value])
        if t in self._dict:
            return self._dict[tuple([key,value])]
        return set()

    def filter(self,token):
        return set.intersection(*(self.get(key,value) for key, value in token.items()))


def token_create_node(node):
    attrs = node.get_nonempty_scalar_attributes()
    return Token({'create_node':node,'modified_attrs':tuple(attrs)})

def token_edit_attrs(node,attrlist):
    return Token({'node':node,'modified_attrs':tuple(attrlist)})

def token_delete_node(node):
    return Token({'delete_node':node})

def token_create_edge(node1,attr1,attr2,node2):
    return Token({'create_edge':(node1,attr1,attr2,node2)})

def token_delete_edge(node1,attr1,attr2,node2):
    return Token({'delete_edge':(node1,attr1,attr2,node2)})
