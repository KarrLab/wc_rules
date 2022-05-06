from dataclasses import dataclass
from ..utils.collections import DictLike, listmap, Mapping, merge_dicts, no_overlaps, merge_lists
from itertools import chain, repeat,starmap
from typing import Tuple, Any
from ..schema.actions import AddNode, AddEdge
from copy import deepcopy
from ..utils.random import generate_id
from collections import UserDict

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

    def nodes(self):
        return (self.ports[0].node,self.ports[1].node)

    def attrs(self):
        return (self.ports[0].attr,self.ports[1].attr)

    def remap(self,d):
        n1,e1,n2,e2 = self.unpack()
        return self.__class__.create(d[n1],e1,d[n2],e2)

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

    def remap(self,d):
        n,a,v = self.unpack()
        return self.__class__(d[n],a,v)


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

    # def generate_actions(self,generator,count=1):
    #     idxs = self._dict.keys()
    #     node_classes = {idx:node.__class__ for idx, node in self.iter_nodes()}
    #     node_attributes = {idx:node.get_literal_attrdict(ignore_id=True,ignore_None=True) for idx, node in self.iter_nodes()}
    #     edges = [e.unpack() for e in self.iter_edges()]
    #     for _ in range(count):
    #         idxmap = dict(zip(idxs,[generator.generate_id() for _ in range(len(idxs))]))
    #         for idx in idxs:
    #             yield AddNode(node_classes[idx],idxmap[idx],deepcopy(node_attributes[idx]))
    #         for n1,e1,n2,e2 in edges:
    #             yield AddEdge(idxmap[n1],e1,idxmap[n2],e2)

    def generate_actions(self):
        for idx,node in self.iter_nodes():
            attrs = deepcopy(node.get_literal_attrdict(ignore_id=True,ignore_None=True))
            yield AddNode(node.__class__,idx,attrs)
        for e in self.iter_edges():
            yield AddEdge(*e.unpack())
        

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

    def join(self,other):
        assert no_overlaps([self._dict,other._dict])
        self._dict = merge_dicts([self._dict,other._dict])
        return self

    @classmethod
    def initialize_from(cls,classes,names,edges=[],literal_attrs=[]):
        g = cls([c(n) for c,n in zip(classes,names)])
        for e in edges:
            g.add_edge(*e)
        for a in literal_attrs:
            g.set_attr(*a)
        return g

    @classmethod
    def compose_from(cls,*graphs):
        return cls(merge_lists([x.duplicate().values() for x in graphs]))

    def add_attribute(self,node_name,attr,value):
        self[node_name].safely_set_attr(attr,value)
        return self

    def add_edge(self,node1,attr,node2):
        self[node1].safely_add_edge(attr,self[node2])
        return self

    def set_attr(self,node,attr,value):
        self[node].safely_set_attr(attr,value)
        return self

    def add_edges(self,edges):
        for e in edges:
            self.add_edge(*e)
        return self

    def set_attrs(self,attrs):
        for a in attrs:
            self.set_attr(*a)
        return self

class GraphFactory(GraphContainer):

    def generate_actions(self,n=1):
        actions = list(GraphContainer.generate_actions(self))
        native_ids = self.keys()
        for i in range(n):
            idmap = dict(zip(native_ids,[generate_id() for _ in range(len(native_ids))]))
            for action in actions:
                yield action.remap(idmap)


class GraphLoader:

    def __init__(self,graphcounts):
        for g,n in graphcounts:
            assert isinstance(g,GraphFactory) and isinstance(n,int)
        self.items = graphcounts

    def generate_actions(self):
        for g,n in self.items:
            for act in g.generate_actions(n):
                yield act




@dataclass(eq=True,order=True,frozen=True)
class TextualForm:
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
    def create(cls,g):
        names = sorted(g._dict.keys())
        classes = tuple([g[x].__class__ for x in order])
        attrs = tuple(sorted(g.iter_literal_attrs()))
        edges = tuple(sorted(g.iter_edges()))
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

    def remap(self,d):
        names = [d[x] for x in self.names]
        classes = self.classes
        attrs = [x.remap(d) for x in self.attrs]
        edges = [x.remap(d) for x in self.edges]
        return self.__class__(names,classes,attrs,edges)

@dataclass(eq=True,order=True,frozen=True)
class CanonicalForm(TextualForm):
    
    @classmethod
    def create(cls,g,order,mapping):
        names = mapping*order
        classes = tuple([g[x].__class__ for x in order])
        attrs = tuple(sorted([x.duplicate(mapping) for x in g.iter_literal_attrs()]))
        edges = tuple(sorted([x.duplicate(mapping) for x in g.iter_edges()]))
        return cls(names,classes,attrs,edges)


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
    