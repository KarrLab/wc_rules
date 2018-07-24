from abc import ABC, abstractmethod
import random


class Pattern(object):
    def __init__(self,name,nodes=None):
        self.name = name
        self.nodes = dict()
        if nodes is not None:
            self.add_nodes(nodes,recurse=True)

    def add_nodes(self,nodes,recurse=True):
        for node in nodes:
            idx = node.get_id()
            if idx in self.nodes:
                continue
            if idx not in self.nodes:
                self.nodes[idx] = node
            if recurse:
                related_attrs = (x for x in node.attribute_properties
                    if node.attribute_properties[x]['related']
                    and getattr(node,x) is not None)
                for attr in related_attrs:
                    if node.attribute_properties[attr]['append']:
                        self.add_nodes(getattr(node,attr),recurse)
                    else:
                        self.add_nodes([getattr(node,attr)],recurse)
        return self

class WorkingMemoryGraph(object):
    def __init__(self):
        self.nodes = dict()

    def add_node(self,node):
        self.nodes[node.get_id()] = node
        return self

    def retrieve_node(self,idx=None):
        if idx is None:
            idx = random.choice(list(self.nodes.keys()))
        return self.nodes[idx]

    def __str__(self):
        return self.nodes.__str__()


class PassThroughNode(ABC):
    def __init__(self,children=None):
        self.children = []

    def add_children(self,children):
        for child in children:
            if child not in self.children:
                self.children.append(child)
        return self

    def send_token(self,token,verbose=False):
        for child in self.children:
            # try each child, if it passes through one successfully,
            # forget the others
            if verbose:
                print('Passing from '+ self.namegen()+ ' to ' + child.namegen())
            status = child.process_token(token,verbose)
        return

    @abstractmethod
    def evaluate_token(self,token,verbose=False): pass

    @abstractmethod
    def namegen(self): pass

    def process_token(self,token,verbose=False):
        if verbose:
            print('Checking for '+self.namegen())
        if self.evaluate_token(token,verbose):
            self.send_token(token,verbose)
            return True
        return False

class TypeCheckNode(PassThroughNode):
    def __init__(self,class_obj):
        super().__init__()
        # self.matching_class is the class object against which the type is checked
        self.matching_class = class_obj

    def evaluate_token(self,token,verbose=False):
        value = isinstance(token,self.matching_class)
        if verbose:
            print(value)
        return value

    def namegen(self):
        return "TYPECHECK " + self.matching_class.__name__

class AttrCheckNode(PassThroughNode):
    def __init__(self,attr_check_list):
        super().__init__()
        # self.attr_check_list is a list of (attrname,value,) tuples
        # where the node is checked if it has the same value for the same attr
        self.attr_check_list = attr_check_list

    def evaluate_token(self,token,verbose=False):
        value = all(getattr(token,attrname)==value for attrname,value in self.attr_check_list)
        if verbose:
            print(value)
        return value

    def namegen(self):
        return "ATTRCHECK " + str(self.attr_check_list)

class AlphaTree(dict):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.root = 'Entity'

    def add_patterns(self,patterns):
        nodelist = []
        for pattern in patterns:
            for key in pattern.nodes:
                node = pattern.nodes[key].set_id(pattern.name+'.'+key)
                nodelist.append(node)
        self.build_typecheck_tree(nodelist)
        return self

    def build_typecheck_tree(self,nodes):
        ''' Builds a tree of typechecknodes given a list of pattern nodes '''

        for node in nodes:
            ignore = True
            lastchecked=None
            for class_obj in reversed(node.__class__.__mro__):
                name = class_obj.__name__
                if name == 'Entity':
                    ignore = False
                if ignore:
                    continue
                if name not in self:
                    x = TypeCheckNode(class_obj)
                    self[name] = x
                    if lastchecked is not None:
                        self[lastchecked].add_children([x])
                lastchecked = class_obj.__name__

            scalar_attrs = (x for x in node.attribute_properties
                if x!= 'id'
                and not node.attribute_properties[x]['related']
                and getattr(node,x) is not None
                )

            attr_check_list = sorted([ (attr,getattr(node,attr),) for attr in scalar_attrs])
            x = AttrCheckNode(attr_check_list)
            self[lastchecked].add_children([x])

        return self

    def process_token(self,token,verbose=False):
        if verbose:
            print('Checking instance '+str(token))
        self[self.root].process_token(token,verbose)
        return
