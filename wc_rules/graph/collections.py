from dataclasses import dataclass
from ..utils.collections import DictLike
from typing import Tuple

@dataclass(order=True,frozen=True)
class Port:
    __slots__ = ['node','attr']
    node: str
    attr: str

@dataclass(order=True,frozen=True)
class Edge:
    __slots__ = ['ports']
    ports: Tuple[Port]

    @staticmethod
    def make(n1,e1,n2,e2):
        return Edge(tuple(sorted([Port(n1,e1),Port(n2,e2)])))

    def unpack(self):
        return (self.ports[0].node, self.ports[0].attr, self.ports[1].node, self.ports[1].attr,)

class GraphContainer(DictLike):
    # A temporary container for a graph that can be used to create
    # canonical forms or iterate over a graph

    def __init__(self,_list=[]):
        # there must be only one way to create a GraphContainer and that must be to create a list
        super().__init__(_list)

    def iternodes(self):
        for idx, node in self._dict.items():
            yield idx,node

    def iteredges(self):
        edges_visited = set()
        for idx,node in self.iternodes():
            for attr in node.get_related_attributes(ignore_None=True):
                related_attr = node.get_related_name(attr)
                for related_node in node.listget(attr):
                    edge = Edge.make(node.id, attr,related_node.id,related_attr)
                    if edge not in edges_visited:
                        edges_visited.add(edge)
                        yield edge

    def update(self):
        idx,root = list(self._dict.items())[0]
        for node in root.get_connected():
            self.add(node)

    def duplicate(self,varmap={},include=None):
        if include is None:
            include = self.keys()

        newnodes = dict()
        for idx,node in self.iternodes():
            if idx not in include:
                continue
            idx = varmap.get(idx,idx)
            newnodes[idx] = node.duplicate(id=idx)

        for edge in self.iteredges():
            idx1,attr1,idx2,attr2 = edge.unpack()
            if idx1 not in include or idx2 not in include:
                continue
            idx1, idx2 = [varmap.get(x,x) for x in [idx1,idx2]]
            newnodes[idx1].safely_add_edge(attr1,newnodes[idx2])
        return GraphContainer(newnodes.values())

    def strip_attrs(self):
        attrs = dict()
        for idx,node in self.iternodes():
            attrs[idx] = node.get_literal_attrdict()
            for attr in attrs[idx]:
                setattr(node,attr,None)
        return self,attrs

    def validate_connected(self):
        err = "GraphContainer does not hold a connected graph."
        assert len(self) == 0 or GraphContainer(self.values()[0].get_connected())==self, err

    @property
    def variables(self):
        return self.keys()

    @property
    def namespace(self):
        return {idx:node.__class__ for idx,node in self._dict.items()}
    
    def add_suffix(self,suffix):
        varmap = {x:f'{x}_{suffix}' for x in self.keys()}
        return self.duplicate(varmap=varmap)


@dataclass(unsafe_hash=True)
class CanonicalForm:
    partition: tuple
    classes: tuple
    leaders: tuple
    edges: tuple

    @property
    def namespace(self):
        return dict(zip(merge_lists(self.partition),self.classes))
    

@dataclass(unsafe_hash=True)
class SymmetryGenerator:
    source: tuple
    targets: tuple
    