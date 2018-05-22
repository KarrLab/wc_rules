"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""
import inspect
from wc_rules.indexer import BooleanIndexer

class ClassQuery(object):
    def __init__(self,_class):
        if not inspect.isclass(_class):
            raise utils.IndexerError('ClassQuery init method needs a class as argument')
        self._class = _class
        self.indexer = BooleanIndexer()
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
