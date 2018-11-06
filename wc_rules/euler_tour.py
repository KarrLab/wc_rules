from blist import blist
from .utils import generate_id, AddError
from .indexer import SetLike, DictLike
import random

class EulerTour(object):
    def __init__(self,id=None,iterable=None,edges=None,spares=None):
        self.id = id if id is not None else generate_id()
        self._tour = blist(iterable) if iterable is not None else blist()
        self._edges = set(edges) if edges is not None else set()
        self._spares = set(spares) if spares is not None else set()

    # Magic methods
    def __contains__(self,node):
        return node in self._tour

    def __len__(self):
        return len(self._tour)

    def __str__(self):
        return ' '.join([x.id for x in self._tour]+['spares =',str(len(self._spares))])

    def __getitem__(self,key):
        return self._tour[key]

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

    def find_sequence(self,sequence):
        for i in range(len(self)-len(sequence)+1):
            if self._tour[i:i+len(sequence)]==sequence:
                return i
        return None

    def is_rooted_at(self,node):
        return self._tour[0] == self._tour[-1] == node

    # Basic modifications
    def reroot(self,node1,node2=None):
        # tour is a blist
        i = None
        if node2 is None:
            i= self.first_occurrence(node1)
        else:
            i= self.find_sequence([node1,node2])
        if i!=0:
            self.rotate(i)
        return self

    def rotate(self,i):
        tour = self._tour
        self._tour = tour[i:] + tour[1:i] + [tour[i]]
        return self

    def add_spares(self,spares):
        for spare in spares:
            self._spares.add(spare)
        return self

    def add_edges(self,edges):
        for edge in edges:
            self._edges.add(edge)
        return self

    def remove_spares(self,spares):
        for spare in spares:
            self._spares.remove(spare)
        return self

    def remove_edges(self,edges):
        for edge in edges:
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

    def add_tour(self,tour):
        assert tour not in self
        self.add(tour)
        return self

    def remove_tour(self,tour):
        assert tour in self
        self.remove(tour)
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

    # Sorting tours
    def sort_tours(self,tours):
        return sorted(tours,key=self.sortkeygen,reverse=True)

    @staticmethod
    def sortkeygen(x):
        first = len(x)
        second = x[0]
        if hasattr(x[0],'id'):
            second = x[0].id
        return [first,second]

    # Creating new tours from singleton nodes
    def create_new_tour_from_node(self,node):
        if type(node) not in [int,float,str]:
            assert len(node.get_nonempty_related_attributes())==0
        assert self.get_mapped_tour(node) is None
        t = EulerTour(None,[node])
        self.add_new_tour(t)
        return self

    def delete_existing_tour_from_node(self,node):
        if type(node) not in [int,float,str]:
            assert len(node.get_nonempty_related_attributes())==0
        t = self.get_mapped_tour(node)
        self.delete_existing_tour(t)
        return self

    # Shortcut add and delete (to use for testing)
    def add_new_tour(self,tour):
        self.add_tour(tour)
        self.remap_nodes(tour.get_nodes(),tour)
        return self

    def delete_existing_tour(self,tour):
        self.remove_tour(tour)
        self.remap_nodes(tour.get_nodes())
        return self

    # Basic link: t1,t2 --> t
    def link(self,t1,t2,u,v):
        t1.reroot(u)
        t2.reroot(v)
        return EulerTour(None,t1._tour + t2._tour + [u])

    #Basic cut: t-->t1,t2
    def cut(self,t,u,v):
        t.reroot(u,v)
        assert u in t and v in t
        v2 = t.last_occurrence(v)
        inner = t._tour[1:v2+1]
        outer = t._tour[v2+1:]
        assert inner[0] == inner[-1] == v
        assert outer[0] == outer[-1] == u
        sorted_tours = [EulerTour(None,x) for x in self.sort_tours([inner,outer])]
        return sorted_tours

    def find_edge(self,node1,node2):
        x1 = self.get_mapped_tour(node1)
        x2 = self.get_mapped_tour(node2)
        assert None not in [x1,x2]
        if x1==x2:
            return [x1]
        return [x1,x2]

    # Augmented link
    # if edge in t, add edge to t._spares
    # if edge
    def auglink(self,edge):
        node1,attr1,attr2,node2 = edge
        tours = self.find_edge(node1,node2)
        if len(tours)==1:
            tours[0].add_spares([edge])
            return self
        big,small = self.sort_tours(tours)
        if big !=tours[0]:
            node1,node2 = node2,node1

        t = self.link(big,small,node1,node2)
        big._tour = t._tour
        big.add_edges(small._edges | set([edge]))
        big.add_spares(small._spares)
        self.remap_nodes(small.get_nodes(),big)
        self.remove_tour(small)
        return self

    # Augmented cut
    # if edge in t._spares, simply remove
    # if edge in t._edges, do cut--> t1,t2
    #      if exists spanning edge in t._spares, remerge t1,t2
    #      else return t1,t2
    def augcut(self,edge):
        node1,attr1,attr2,node2 = edge
        tour = self.find_edge(node1,node2)[0]
        if edge in tour._spares:
            tour.remove_spares([edge])
            return self
        big,small = self.cut(tour,node1,node2)
        if len(tour._spares)!=0:
            # pop a spare, remerge
            for spare in tour._spares:
                if spare[0] in big and spare[3] in small:
                    new_tour = self.link(big,small,spare[0],spare[3])
                    tour._tour = new_tour._tour
                    tour.remove_spares([spare])
                    tour.remove_edges([edge])
                    tour.add_edges([spare])
                    # no remapping required
                    return self
                if spare[3] in big and spare[0] in small:
                    new_tour = self.link(big,small,spare[3],spare[0])
                    tour._tour = new_tour._tour
                    tour.remove_spares([spare])
                    tour.remove_edges([edge])
                    tour.add_edges([spare])
                    # no remapping required
                    return self
                # if you're here, then no available spare to remerge

        # populate edges and spares
        b,s = big._tour, small._tour

        edges1 = [x for x in tour._edges if x[0] in b and x[3] in b]
        edges2 = [x for x in tour._edges if x[0] in s and x[3] in s]
        assert len(edges1) + len(edges2) + 1 == len(tour._edges)

        spares1 = [x for x in tour._spares if x[0] in b and x[3] in b]
        spares2 = [x for x in tour._spares if x[0] in s and x[3] in s]
        assert len(spares1) + len(spares2) == len(tour._spares)

        # Finalize cut
        tour._tour = big._tour
        tour._edges = set(edges1)
        tour._spares = set(spares1)
        small._edges = set(edges2)
        small._spares = set(spares2)
        self.remap_nodes(small.get_nodes(),small)
        self.add_tour(small)
        return self
