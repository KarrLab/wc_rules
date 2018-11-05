from blist import blist
from .utils import generate_id, AddError
from .indexer import SetLike, DictLike
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

    # Access methods
    def get_nodes(self):
        return set(self._tour)

    def get_edges(self):
        return self._edges

    def get_spares(self):
        return self._spares

    # Search methods
    def first_occurrence(self,node):
        if node in self:
            return self._tour.index(node)
        return None
    def last_occurrence(self,node):
        if node in self:
            for i,x in reversed(list(enumerate(self._tour))):
                if x==node:
                    return i
        return None

    # Basic modifications
    def reroot(self,node):
        # tour is a blist
        if self._tour[0]==node:
            return self
        i = self.first_occurrence(node)
        tour = self._tour
        self._tour = tour[i:] + tour[1:i] + [tour[i]]
        return self

    def add_spare(self,spare):
        self._spares.add(spare)
        return self

    def add_edge(self,edge):
        self._edges.add(edge)
        return self

    def remove_spare(self,spare):
        self._spares.remove(spare)
        return self

    def remove_edge(self,edge):
        self._edges.remove(edge)
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

    def shrink_left(self,length):
        self.delete_sequence(0,length)
        return self

    def shrink_right(self,length):
        self.delete_sequence(len(self)-length,length)
        return self

    def find_sequence(self,sequence):
        for i in range(len(self)-len(sequence)):
            if self._tour[i:i+len(sequence)]==sequence:
                return i
        return None

class EulerTourIndex(SetLike):
    def __init__(self):
        super().__init__()
        self._tourmap = dict()

    def map_node_tour(self,node,tour):
        self._tourmap[node] = tour
        return self

    def unmap_node_tour(self,node):
        self._tourmap.pop(node)
        return self

    def remap_nodes(self,nodes,new_tour=None):
        for node in nodes:
            if new_tour is not None:
                self.map_node_tour(node,new_tour)
            else:
                self.unmap_node_tour(node)
        return self

    def get_mapped_tour(self,node):
        return self._tourmap.get(node,None)

    def is_connected(self,nodelist):
        tours = [self.get_mapped_tour(x) for x in nodelist]
        return None not in tours and tours[1:]==tours[:-1]

    def add_tour(self,tour,remap=True):
        assert tour not in self
        self.add(tour)
        if remap:
            self.remap_nodes(tour.get_nodes(),tour)
        return self

    def remove_tour(self,tour,remap=True):
        assert tour in self
        self.remove(tour)
        if remap:
            self.remap_nodes(tour.get_nodes())
        return self

    # Static methods for handling edges
    def flip(edge):
        return tuple(reversed(edge))

    def canonize(self,edge):
        node1,attr1,attr2,node2 = edge
        as_is = (attr1 <= attr2) or (attr1==attr2 and node1.id<node2.id)
        if not as_is:
            return self.flip(edge)
        return edge

    def bigger(self,t1,t2):
        return len(t1) >= len(t2)

    # Link/Cut methods
    def link(self,t1,t2,u,v):
        assert t1 in self and t2 in self
        assert u in t1 and v in t2
        t1.reroot(u)
        t2.reroot(v)
        t1._tour = t1._tour + t2._tour + [u]
        t1._edges = t1._edges | t2._edges
        t1._spares = t1._spares | t2._spares
        self.remap_nodes(t2.get_nodes(),t1)
        self.remove(t2)
        return self
