from dataclasses import dataclass
from ..utils.collections import DictLike, listmap, Mapping
from itertools import chain
from typing import Tuple, Any

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
    def create(n1,e1,n2,e2):
        return Edge(tuple(sorted([Port(n1,e1),Port(n2,e2)])))

    def unpack(self):
        return (self.ports[0].node, self.ports[0].attr, self.ports[1].node, self.ports[1].attr,)

    def duplicate(self,mapping):
        n1,e1,n2,e2 = self.unpack()
        return self.__class__.create(mapping*n1,e1,mapping*n2,e2)        

    def pprint(self):
        n1,e1,n2,e2 = self.unpack()
        return f'{n1}.{e1}--{n2}.{e2}'

@dataclass(order=True,frozen=True)
class Attr:
    __slots__ = ['node','attr','value']
    node: str
    attr: str
    value: Any

    def duplicate(self,mapping):
        return self.__class__(mapping*self.node,self.attr,self.value)

    def unpack(self):
        return (self.node,self.attr,self.value)

    def pprint(self):
        return f'{self.node}.{self.attr}=={self.value}'


class GraphContainer(DictLike):
    # A temporary container for a graph that can be used to create
    # canonical forms or iterate over a graph

    def __init__(self,_list=[]):
        # there must be only one way to create a GraphContainer and that must be to create a list
        super().__init__(_list)

    def iter_nodes(self):
        for idx, node in self._dict.items():
            yield idx,node

    def iter_edges(self):
        visited = set()
        for idx,node in self.iter_nodes():
            for attr,node2 in node.iter_edges():
                edge = Edge.create(idx,attr,node2.id,node.get_related_name(attr))
                if edge not in visited:
                    visited.add(edge)
                    yield edge

    def iter_literal_attrs(self):
        for idx,node in self.iter_nodes():
            for attr in node.get_literal_attributes(ignore_id=True,ignore_None=True):
                yield Attr(idx,attr,node.get(attr))

    def duplicate(self,varmap={},include=None):
        if include is None:
            include = self.keys()

        newnodes = dict()
        for idx,node in self.iter_nodes():
            if idx not in include:
                continue
            idx = varmap.get(idx,idx)
            newnodes[idx] = node.duplicate(id=idx)

        for edge in self.iter_edges():
            idx1,attr1,idx2,attr2 = edge.unpack()
            if idx1 in include and idx2 in include:
                idx1, idx2 = [varmap.get(x,x) for x in [idx1,idx2]]
                newnodes[idx1].safely_add_edge(attr1,newnodes[idx2])
        return GraphContainer(newnodes.values())

    def strip_attrs(self):
        attrs = dict()
        for idx,node in self.iter_nodes():
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

    def pprint(self):
        s = ''
        s += 'Graph\n'
        for idx,node in self.iter_nodes():
            s += f'{idx}:<{node.__class__.__name__}>' + '\n'
        for attr in chain(self.iter_literal_attrs(),self.iter_edges()):
            s += attr.pprint() + '\n'
        return s


@dataclass(eq=True,order=True,frozen=True)
class CanonicalForm:
    __slots__ = ['names','classes','attrs','edges']

    names: Tuple[str]
    classes: Tuple[type]
    attrs: Tuple[Attr]
    edges: Tuple[Edge]

    def pprint(self):
        s = ''
        s += 'CanonicalForm\n'
        for n,c in zip(self.names,self.classes):
            s += f'{n}:<{c.__name__}>' + '\n'
        for a in self.attrs + self.edges:
            s += a.pprint() + '\n'
        return s

    @classmethod
    def create(cls,g,order,mapping):
        names = mapping*order
        classes = tuple([g[x].__class__ for x in order])
        attrs = tuple(sorted([x.duplicate(mapping) for x in g.iter_literal_attrs()]))
        edges = tuple(sorted([x.duplicate(mapping) for x in g.iter_edges()]))
        return cls(names,classes,attrs,edges)

    def build_graph_container(self,mapping=None):
        if mapping is None:
            mapping = Mapping.create(self.names)
        g = GraphContainer([c(n) for c,n in zip(self.classes,mapping*self.names)])
        for attr in self.attrs:
            n,a,v = attr.unpack()
            g[mapping.get(n)].safely_set_attr(a,v)
        for edge in self.edges:
            n1,a1,n2,a2 = edge.unpack()
            g[mapping.get(n1)].safely_add_edge(a1,g[mapping.get(n2)])
        return g

@dataclass(unsafe_hash=True)
class CanonicalForm2:
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
    