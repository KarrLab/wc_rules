from .utils import generate_id

class Token(object):
    def __init__(self,contents=None):
        self.id = generate_id()
        self._dict = dict()
        self._location = None
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
        for key,value in tok._dict.items():
            self.__setitem__(key,value)
        return self

    def subset(self,keys):
        return { k:self[k] for k in keys }

    def prep_safe_delete(self):
        for value in self._dict.values():
            if hasattr(value,'_tokens'):
                value._tokens.remove(self)
        return self

    def items(self): return self._dict.items()

    def modify_with_keymap(self,keymap):
        keys = list(self.keys())
        for key in keys:
            self[keymap[key]] = self[key]
            del self[key]
        return self


class TokenRegister(object):
    def __init__(self):
        self._dict = dict()
        self._set = set()

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
        token._location = self
        return self

    def remove_token(self,token):
        if token in self._set:
            token._location = None
            for (key,value) in token.items():
                self.deregister(key,value,token)
            self._set.remove(token)
        return self
