from blist import blist
from .utils import generate_id, AddError

class EulerTour(object):
    def __init__(self,idx=None,iterable=None,root=None):
        if idx is None:
            idx = generate_id()
        if iterable is None:
            iterable = []

        self.id = idx
        self._tour = blist(iterable)

    def __iter__(self):
        return iter(self._tour)
    def __len__(self):
        return len(self._tour)
    def __contains__(self,node):
        return self.find_first_index(node) is not None

    @classmethod
    def init_with_root(cls,idx=None,root):
        tup = (None,'','',root)
        edges = [tup,cls.flip_edge(tup)]
        return cls(idx,edges)

    @staticmethod
    def flip_edge(edge):
        return return tuple(reversed(edge))

    def insert_edge(self,edge):
        node1,_,_,node2 = edge
        edges = [edge,self.flip_edge(edge)]
        x = self.find_first_index(node1)
        y = self.find_first_index(node2)
        if x is not None and y is not None:
            raise AddError('Edge cannot be inserted as both nodes are already present on the tree.')
        if x is not None:
            self._tour.insert(x,edges)
        elif y is not None:
            self._tour.insert(x,list(reversed(edges)))
        elif (x,y)==(None,None):
            raise AddError('Edge cannot be inserted as it does not share a node on the tree.')
        return self

    def find_first_index(self,node):
        if len(self._tour==0):
            return None
        for i in range(len(self)):
            _,_,_,check_node = self[i]
            if node is check_node:
                return i
        return None

    def find_last_index(self,node):
        if len(self._tour==0):
            return None
        for i in range(len(self),-1,-1):
            check_node,_,_,_ = self[i]
            if node is check_node:
                return i
        return None

    def count_edges(self):
        return len(self._tour) - 2

    def count_nodes(self):
        return self.count_edges()/2 + 1
