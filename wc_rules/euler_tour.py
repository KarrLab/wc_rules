from blist import blist
from .utils import generate_id, AddError
import random

class EulerTour(object):
    def __init__(self,id=None,iterable=None,edges=None,spares=None):
        self.id = id if id is not None else generate_id()
        self._tour = blist(iterable) if iterable is not None else blist()
        self._edges = edges if edges is not None else set()
        self._spares = spares if spares is not None else set()

    def __contains__(self,node):
        return node in self._tour

    def __len__(self):
        return len(self._tour)

    def __str__(self):
        return ' '.join([x.id for x in self._tour]+['spares =',str(len(self._spares))])

    def first_occurrence(self,node):
        if node in self:
            return self._tour.index(node)
        return None

    def last_occurrence(self,node):
        if node in self:
            return self._tour.index(node,-1,-1)
        return None

    @staticmethod
    def flip(edge):
        return tuple(reversed(edge))

    @staticmethod
    def canonize(edge):
        node1,attr1,attr2,node2 = edge
        as_is = (attr1 <= attr2) or (attr1==attr2 and node1.id<node2.id)
        if not as_is:
            return self.flip(edge)
        return edge

    def insert_sequence(self,index,nodes):
        for i in range(len(nodes)):
            self._tour.insert(index+i,nodes[i])
        return self

    def insert_edge(self,edge):
        edge = self.canonize(edge)
        node1,attr1,attr2,node2 = edge

        x1 = self.first_occurrence(node1)
        x2 = self.first_occurrence(node2)
        if x1 is not None and x2 is not None:
            self._spares.add(edge)
        elif x2 is None:
            self.insert_sequence(x1+1,[node2,node1])
            self._edges.add(edge)
        else:
            self.insert_sequence(x2+1,[node1,node2])
            self._edges.add(edge)
        return self

    def reroot(self,node):
        i = self.first_occurrence(node)
        A = self._tour[1:i] + [node]
        B = self._tour[i:len(self)]
        self._tour = B + A
        return self
