"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""

class Indexer(dict):

    def __init__(self):
        self._values = {}

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

    def update(self,dict_obj):
        for key,val in dict_obj.items():
            self.update_key_value(key,val)
        return self
