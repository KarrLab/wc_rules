"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

import networkx
import obj_model.core
import wc_rules.mol_schema


class GraphMeta(obj_model.core.Model.Meta):
    """ Inner class to annotate the properties which represent the semantic meaning of each node and the 
    edges of the object graph.

    Attributes:
        outward_edges (:obj:`tuple` of :obj:`str`): list of names of attributes to be examined recursively
            for get_edges(). Only :obj:`obj_model.core.RelatedManager` attributes allowed.
        semantic (:obj:`tuple` of :obj:`str`): list of names of attributes/properties should be examined
            for node_match(). Only attributes/properties that return values comparable by '==' allowed.    
    """
    outward_edges = tuple()
    semantic = tuple()


def node_match(node1, node2):
    """ Determine if two nodes are semantically equal

    Args:        
        node1 (:obj:`wc_rules.mol_schema.BaseClass`): from the bigger graph
        node2 (:obj:`wc_rules.mol_schema.BaseClass`): from the smaller graph

    Returns:
        :obj:`bool`: if :obj:`node1` and :obj:`node2` are semantically equal
    """
    return node2.node_match(node1)


def node_compare(current, other):
    """ Can current node's semantic properties be entirely contained within other node?

    current --- None returns False
    current --- other returns False if
        other is not an instance of type(current) or any subclass thereof
    current --- other returns False if
        attributes in 'semantic' list (see GraphMeta class) do not match in value, i.e.
           None --- anything is a match
           current.attrib --- None is not a match
           current.attrib == current.attrib is a match

    Args:
        current (:obj:`wc_rules.mol_schema.BaseClass`): ??
        other (:obj:`wc_rules.mol_schema.BaseClass`): ??

    Returns:
        :obj:`bool`: ??
    """
    if other is None:
        return False
    if isinstance(other, (current.__class__,)) is not True:
        return False
    for attrname in current.__class__.GraphMeta.semantic:
        current_attr = getattr(current, attrname)
        other_attr = getattr(other, attrname)
        if current_attr is not None:
            if other_attr is None:
                return False
        if current_attr != other_attr:
            return False
    return True


def get_graph(node, recurse=True, memo=None):
    """

    Args:
        node (:obj:`wc_rules.mol_schema.BaseClass`): node
        recurse (:obj:`bool`, optional): ??
        memo (:obj:`networkx.DiGraph`, optional): ??

    Returns:
        :obj:`networkx.DiGraph`: graph
    """
    def update_graph(graph, obj1):
        if id(obj1) not in graph:
            graph.add_node(id(obj1), obj=obj1)
        else:
            graph.node[id(obj1)]['obj'] = obj1

    # Initializing if a memo is not provided
    if memo is None:
        memo = networkx.DiGraph()
    # Adding node if not already in memo, else updating it
    update_graph(memo, node)

    # getting list of next nodes to check
    next_nodes = []
    for attrname in node.__class__.GraphMeta.outward_edges:
        if getattr(node, attrname) is not None:
            attr = getattr(node, attrname)
            if isinstance(attr, list):
                next_nodes.extend(attr)
            else:
                next_nodes.append(attr)

    # for each node in next_nodes,
    # if an edge already exists, ignore
    # if adding a new edge, recurse onto that node using current memo
    for x in next_nodes:
        update_graph(memo, x)
        e = tuple([id(node), id(x)])
        if e not in memo.edges():
            memo.add_edge(*e)
            if recurse is True:
                memo2 = x.get_graph(recurse=True, memo=memo)
                memo = memo2
    return memo
