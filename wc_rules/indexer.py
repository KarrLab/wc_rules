"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""

class Indexer(dict):

    def __init__(self):
        self._values = {}
        self.last_updated = set()
        self.last_deleted = set()

    def key_exists(self,key):
        return key in self

    def value_exists(self,value):
        return value in self._values

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

    def update_key_value(self,key,value):
        if self.key_exists(key):
            self.delete_key(key)
        self.create_new_key_value(key,value)
        return self

    def append_key_to_last_updated(self,key):
        self.last_updated.add(key)
        return self

    def append_key_to_last_deleted(self,key):
        self.last_deleted.add(key)
        return self

    # Methods available to paired queryobjects
    def update(self,dict_obj):
        for key,val in dict_obj.items():
            self.update_key_value(key,val)
            self.append_key_to_last_updated(key)
        return self

    def remove(self,keylist):
        for key in keylist:
            self.delete_key(key)
            self.append_key_to_last_deleted(key)
        return self

    def flush(self):
        self.last_updated.clear()
        self.last_deleted.clear()
        return self

class ClassQuery(object):
    def __init__(self,_class):
        self._class = _class
        self.indexer = Indexer()
        self.func = lambda x:isinstance(x,self._class)

    def verify(self,obj):
        return self.func(obj)

    def update(self,*id_list):
        n = len(id_list)
        tuplist = zip(id_list,[True]*n)
        self.indexer.update(dict(tuplist))
        return self

    def remove(self,*id_list):
        self.indexer.remove(id_list)
        return self
