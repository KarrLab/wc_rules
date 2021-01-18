from lark import Lark, tree, Transformer,Visitor, v_args, Tree,Token
from dataclasses import dataclass
from collections import deque, ChainMap
from types import MethodType
from abc import ABC, abstractmethod
from obj_model import core

############ ACTION GRAMMER ###################
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
############## Simulator Actions
class SimulatorAction:
    pass

RollbackAction = type('RollbackAction',(SimulatorAction,),{})
TerminateAction = type('TerminateAction',(SimulatorAction,),{})
def rollback(expr):
    assert isinstance(expr,bool), "Rollback condition must evaluate to a boolean."
    return {True:RollbackAction(),False:[]}[expr]
def terminate(expr):
    assert isinstance(expr,bool), "Terminate condition must evaluate to a boolean."
    return {True:TerminateAction(),False:[]}[expr]


############## Primary Actions
# NodeAction -> AddNode, RemoveNode
# SetAttr
# EdgeAction -> AddEdge, RemoveEdge
# make(...) -> primary constructor
# execute(sim) -> executes the action on a simulation state
# rollback(sim) -> rolls back the action on a simulation state


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
    def make(cls,_class,idx,attrs=dict()):
        return cls(_class=_class,idx=idx,attrs=attrs)
    
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
        return cls(idx=node.id,
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
            source_idx = source.id,
            source_attr = attr,
            target_idx = target.id,
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

class CompositeAction(ABC):
    @abstractmethod
    def expand(self):
        pass

############## Literal Attr Actions ###########
@dataclass
class RemoveLiteralAttr(CompositeAction):
    source: 'typing.Any'
    attr: str

    def expand(self):
        return SetAttr.make(self.source,self.attr,None)

@dataclass
class Flip(CompositeAction):
    source: 'typing.Any'
    attr: str

    def expand(self):
        return SetAttr.make(self.source,self.attr,not self.source.get(self.attr))    

@dataclass
class SetTrue(CompositeAction):
    source: 'typing.Any'
    attr: str

    def expand(self):
        return SetAttr.make(self.source,self.attr,True)

@dataclass
class SetFalse(CompositeAction):
    source: 'typing.Any'
    attr: str

    def expand(self):
        return SetAttr.make(self.source,self.attr,False)

@dataclass
class Increment(CompositeAction):
    source: 'typing.Any'
    attr: str
    value: 'typing.Any' = 1

    def expand(self):
        return SetAttr.make(self.source,self.attr,self.source.get(self.attr) + self.value)

@dataclass
class Decrement(CompositeAction):
    source: 'typing.Any'
    attr: str
    value: 'typing.Any' = 1

    def expand(self):
        return SetAttr.make(self.source,self.attr,self.source.get(self.attr) - self.value)

    
######## Edge Attr ##########
@dataclass
class RemoveEdgeAttr(CompositeAction):
    source: 'typing.Any'
    attr: str

    def expand(self):
        return [RemoveEdge.make(self.source,self.attr,x) for x in self.source.listget(self.attr)]

@dataclass
class RemoveAllEdges(CompositeAction):
    source: 'typing.Any'

    def expand(self):
        attrs = self.source.get_related_attributes(ignore_None=True)
        return [RemoveEdgeAttr(self.source,attr) for attr in attrs]

######### Node Remove ###########
@dataclass
class Remove(CompositeAction):
    source: 'typing.Any'

    def expand(self):
        return [RemoveAllEdges(self.source), RemoveNode.make(self.source)]


############### codegeneration for methods

class ActionMixin:

    
    def attach_actions(self):
        self.attach_removenode_method()
        for attr,value in self.__class__.Meta.local_attributes.items():
            if attr == 'id':
                continue
            methods = {
                core.LiteralAttribute: self.attach_literalsetattr_method,
                core.NumericAttribute: self.attach_numericattr_methods,
                core.BooleanAttribute: self.attach_booleanattr_methods,
                core.RelatedAttribute: self.attach_edgeattr_methods,
            }

            for attrtype,method in methods.items():
                if isinstance(value.__dict__['attr'],attrtype):
                    method(attr)

    def attach_method(self,name,fn):
        fn.__name__ = name
        fn._is_action = True
        setattr(self,name,MethodType(fn, self))
        return self

    def attach_literalsetattr_method(self,attr):
        def setterfn(self,value):
            return SetAttr.make(self,attr,value)
        def removefn(self):
            return SetAttr.make(self,attr,None)
        self.attach_method('set_{0}'.format(attr),setterfn)
        self.attach_method('remove_{0}'.format(attr),removefn)    
        return self

    def attach_numericattr_methods(self,attr):
        def incrementfn(self,value=None):
            if value is None:
                return Increment(self,attr)
            return Increment(self,attr,value)
        def decrementfn(self,value=None):
            if value is None:
                return Decrement(self,attr)
            return Decrement(self,attr,value)
    
        self.attach_method('increment_{0}'.format(attr),incrementfn)
        self.attach_method('decrement_{0}'.format(attr),decrementfn)    
        return self

    def attach_booleanattr_methods(self,attr):
        def settruefn(self):
            return SetTrue(self,attr)
        def setfalsefn(self):
            return SetFalse(self,attr)
        def flipfn(self):
            return Flip(self,attr)
        self.attach_method('setTrue_{0}'.format(attr),settruefn)
        self.attach_method('setFalse_{0}'.format(attr),setfalsefn)
        self.attach_method('flip_{0}'.format(attr),flipfn)
        return self

    def attach_edgeattr_methods(self,attr):
        def add_edge_fn(self,*args):
            targets = deque()
            for arg in args:
                if isinstance(arg,list):
                    for elem in arg:
                        targets.append(elem)
                else:
                    targets.append(arg)
            return [AddEdge.make(self,attr,x) for x in targets]
            
        def remove_edge_fn(self,*args):
            targets = deque()
            if len(args)==0:
                return RemoveEdgeAttr(self,attr)
            for arg in args:
                if isinstance(arg,list):
                    for elem in arg:
                        targets.append(elem)
                else:
                    targets.append(arg)
            return [RemoveEdge.make(self,attr,x) for x in targets]
            
        self.attach_method('add_{0}'.format(attr),add_edge_fn)
        self.attach_method('remove_{0}'.format(attr),remove_edge_fn)
        return self

    def attach_removenode_method(self):
        def remove_edges_fn(self):
            return RemoveAllEdges(self)

        def removefn(self):
            return Remove(self)

        self.attach_method('remove_all_edges',remove_edges_fn)
        self.attach_method('remove',removefn)
        return self