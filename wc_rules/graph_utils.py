"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
import networkx as nx


class GraphMeta(object):
    """ Inner class holding values used in graph methods

    Attributes:
        outward_edges (:obj:`str`): attributes to be examined recursively for get_graph().
            Only RelatedManager attributes allowed.
        semantic (:obj:`str`): attributes/properties should be examined for node_match().
            Only attributes/properties that return values comparable by '==' allowed.	
    """
    outward_edges = tuple()
    semantic = tuple()


def node_match(node1, node2):
    # this is to be compatible with networkx's subgraph isomorphism algorithm
    # node2 is from the smaller graph
    # node1 is from the bigger graph, whose subgraphs are being questioned
    return node_compare(node2['obj'], node1['obj'])


def edge_match(dict1, dict2):
    return dict1 == dict2


class GraphMatcher(nx.algorithms.isomorphism.DiGraphMatcher):

    def __init__(self, g1, g2):
        super(GraphMatcher, self).__init__(g1, g2, node_match=node_match, edge_match=edge_match)


def node_compare(current, other):
    # Logic: can current node's semantic properties be entirely contained within other node?
    # other must be an instance of current.__class__ or any of its subclasses
    # current's attributes, if specified, must entirely match other's

    def type_match(current, other):
        return isinstance(other, (current.__class__,))

    def attr_match(current, other, attrname):
        is_unspecified = getattr(current, attrname, None) is None
        is_matched = getattr(current, attrname, None) == getattr(other, attrname, None)
        return is_unspecified or is_matched
    def attrs_match(current, other):
        attrlist = current.__class__.GraphMeta.semantic
        return all(attr_match(current, other, x) for x in attrlist)

    def filter_match(current, other):
        if hasattr(current, 'value') and hasattr(other, 'value'):
            return current.compare_values(other.value)
        return True

    funcs = [type_match, attrs_match, filter_match]
    for f in funcs:
        if f(current, other) == False:
            return False
    return True


def get_graph(current_obj, recurse=True, memo=None):
    def update_graph(graph, obj1):
        if id(obj1) not in graph:
            graph.add_node(id(obj1), obj=obj1)
        else:
            graph.node[id(obj1)]['obj'] = obj1

    # Initializing if a memo is not provided
    if memo is None:
        memo = nx.DiGraph()
    # Adding node if not already in memo, else updating it
    update_graph(memo, current_obj)

    # getting list of next nodes to check
    # and the relationship to those nodes
    next_nodes = []
    node_relation = {}
    outward_edges = []
    outward_edges.extend(current_obj.__class__.GraphMeta.outward_edges)

    for attrname, props in self.attribute_properties:
        if props['variable']:
            outward_edges.append(attrname)

    for attrname in current_obj.__class__.GraphMeta.outward_edges:
        if getattr(current_obj, attrname) is not None:
            attr = getattr(current_obj, attrname)
            if isinstance(attr, list):
                next_nodes.extend(attr)
                for a in attr:
                    node_relation[a] = attrname
            else:
                next_nodes.append(attr)
                node_relation[attr] = attrname

    # for each node in next_nodes,
    # if an edge already exists, ignore
    # if adding a new edge, recurse onto that node using current memo
    for x in next_nodes:
        update_graph(memo, x)
        e = tuple([id(current_obj), id(x)])
        if e not in memo.edges():
            memo.add_edge(*e, relation=node_relation[x])
            if recurse is True:
                memo2 = x.get_graph(recurse=True, memo=memo)
                memo = memo2
    return memo
