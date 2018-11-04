from blist import blist
from .utils import generate_id, AddError
import random

class EulerTour(object):
    def __init__(self,id=None,iterable=None,edges=None,spares=None):
        self.id = id if id is not None else generate_id()
        self._tour = blist(iterable) if iterable is not None else blist()
        self._edges = edges if edges is not None else set()
        self._spares = spares if spares is not None else set()

    # Magic methods
    def __contains__(self,node):
        return node in self._tour

    def __len__(self):
        return len(self._tour)

    def __str__(self):
        return ' '.join([x.id for x in self._tour]+['spares =',str(len(self._spares))])

    # Static methods for handling edges
    def flip(edge):
        return tuple(reversed(edge))
    def canonize(edge):
        node1,attr1,attr2,node2 = edge
        as_is = (attr1 <= attr2) or (attr1==attr2 and node1.id<node2.id)
        if not as_is:
            return self.flip(edge)
        return edge

    # Search methods
    def first_occurrence(self,node):
        if node in self:
            return self._tour.index(node)
        return None
    def last_occurrence(self,node):
        if node in self:
            for i in range(len(self),-1,-1):
                if self[i]==node:
                    return i
        return None

    # Basic modifications
    def reroot(self,node):
        # tour is a blist
        if self._tour[0]==node:
            return tour
        i = self.first_occurrence(node)
        tour = self._tour
        self._tour = tour[i:] + tour[1:i] + [tour[i]]
        return self

    def insert_sequence(self,idx,nodes):
        assert 0 <= idx <= len(self)
        self._tour = self._tour[:idx] + blist(nodes) + self._tour[idx:]
        return self

    def delete_sequence(self,idx,length):
        assert 0 <= idx < idx+length <= len(self)
        self._tour = self._tour[:idx] + self._tour[idx+length:]
        return self

    def extend_left(self,nodes):
        self.insert_sequence(0,nodes)
        return self

    def extend_right(self,nodes):
        self.insert_sequence(len(self),nodes)
        return self
        
