from lark import Lark, tree, Transformer,Visitor, v_args, Tree,Token
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .base import BaseClass

action_grammar = """
%import common.CNAME
%import common.WS_INLINE
%import common.NUMBER
%ignore WS_INLINE
%import common.ESCAPED_STRING
%import common.NEWLINE

COMMENT: /#.*/
%ignore COMMENT
%ignore NEWLINE


    LITERAL.1: NUMBER | "True" | "False" | ESCAPED_STRING
    SYMBOL:  "==" | "!=" |"<="| ">=" | "<" | ">" | "=" | "," | "+" | "-" | "*" | "/" | "." | "(" | ")"

    variable.1: CNAME
    subvariable: CNAME
    attribute: CNAME    
    action_name: CNAME
    GRAPH_ACTION_NAME: "add" | "remove" | "set"
    
    ?graph_target.1: variable ["." subvariable]
    arg:  graph_target | LITERAL  | expression
    args: arg ("," arg)*
    graph_action.2: variable ["." subvariable]  "." GRAPH_ACTION_NAME ["_" attribute] "(" [args] ")"
    
    kw: CNAME
    kwarg: kw "=" arg
    kwargs: kwarg ("," kwarg)* 
    custom_action: variable ["." subvariable] "." action_name "(" [kwargs] ")"

    ?action.1: graph_action|custom_action

    expression: (LITERAL | SYMBOL | CNAME )+ 
    ?start: action | expression

"""

parser = Lark(action_grammar, start='start')

class DummySimulationState:
    def __init__(self,*args):
        self._dict = {arg.get_id():arg for arg in args}

    def resolve(self,idx):
        return self._dict[idx]

    def update(self,node):
        self._dict[node.id] = node
        return self

    def remove(self,node):
        del self._dict[node.id]
        del node
        return self

    def get_contents(self,ignore_id=True,ignore_None=True,use_id_for_related=True):
        return {x.get_id():x.get_attrdict(ignore_id=ignore_id,ignore_None=ignore_None,use_id_for_related=use_id_for_related) for k,x in self._dict.items()}

class PrimaryAction(ABC):

    @classmethod
    @abstractmethod
    def make(cls,*args,**kwargs):
        pass

    @abstractmethod
    def execute(self,sim):
        pass

    @abstractmethod
    def rollback(self,sim):
        pass

@dataclass
class NodeAction(PrimaryAction):
    _class: type
    idx: str 
    attrs: dict

    def add_node(self,sim):
        #c,i,attrs = self._class,self.idx,self.attrs
        x = self._class(id=self.idx)
        for attr, value in self.attrs.items():
            x.safely_set_attr(attr,value)
        sim.update(x)
        return self

    def remove_node(self,sim):
        sim.remove(sim.resolve(self.idx))
        return self

class AddNode(NodeAction):    

    @classmethod
    def make(cls,*args,**kwargs):
        return cls(*args,**kwargs)
    
    def execute(self,sim):
        self.add_node(sim)
        return self

    def rollback(self,sim):
        self.remove_node(sim)
        return self

class RemoveNode(NodeAction):

    @classmethod
    def make(cls,node):
        return cls(_class=node.__class__,
            idx=node.id,attrs=node.get_literal_attrdict())

    def execute(self,sim):
        self.remove_node(sim)
        return self

    def rollback(self,sim):
        self.add_node(sim)
        return self

@dataclass
class SetAttr(PrimaryAction):
    idx: str
    attr: str
    value: 'typing.Any'
    old_value: 'typing.Any'

    @classmethod
    def make(cls,node,attr,value):
        return cls(idx=node.get_id(),
            attr = attr,
            value = value,
            old_value = node.get(attr)
            )

    def execute(self,sim):
        node = sim.resolve(self.idx)
        node.safely_set_attr(self.attr,self.value)
        return self

    def rollback(self,sim):
        node = sim.resolve(self.idx)
        node.safely_set_attr(self.attr,self.old_value)
        return self

@dataclass
class EdgeAction(PrimaryAction):
    source_idx: str
    source_attr: str
    target_idx: str
    target_attr: str

    @classmethod
    def make(cls,source,attr,target):
        return cls(
            source_idx = source.get_id(),
            source_attr = attr,
            target_idx = target.get_id(),
            target_attr = source.get_related_name(attr)
            )

    def add_edge(self,sim):
        source,target = sim.resolve(self.source_idx), sim.resolve(self.target_idx)
        source.safely_add_edge(self.source_attr,target)
        return self

    def remove_edge(self,sim):
        source,target = sim.resolve(self.source_idx), sim.resolve(self.target_idx)
        source.safely_remove_edge(self.source_attr,target)
        return self

class AddEdge(EdgeAction):
    def execute(self,sim):
        self.add_edge(sim)
        return self

    def rollback(self,sim):
        self.remove_edge(sim)
        return self

class RemoveEdge(EdgeAction):
    def execute(self,sim):
        self.remove_edge(sim)
        return self

    def rollback(self,sim):
        self.add_edge(sim)
        return self

class SecondaryAction(ABC):
    @abstractmethod
    def expand(self,sim):
        pass