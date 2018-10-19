from .indexer import DictSet
from .rete_nodes import Root

from . import gml

from collections import deque

class ReteNet(DictSet):
    def __init__(self):
        super().__init__([Root()])

    def add_node(self,node):
        return self.add(node)

    def add_edge(self,node1,node2):
        self.add_node(node1)
        self.add_node(node2)
        node1.successors.add(node2)
        node2.predecessors.add(node1)
        return self

    def get_root(self):
        return self['root']

    def depth_first_search(self,start_node):
        # return depth-first exploration of graph as an iter
        visited = set()
        next_nodes = deque()
        next_nodes.appendleft(start_node)
        while len(next_nodes) > 0:
            current_node = next_nodes.popleft()
            suc = current_node.successors - visited
            suc2 = sorted(suc,reverse=True,key=str)
            next_nodes.extendleft(suc2)
            visited.add(current_node)
            yield current_node

    def draw_as_gml(self,filename=None,as_string=False):
        node_labels, node_categories, idx_dict = dict(),dict(),dict()
        edge_tuples = list()
        start_node = self.get_root()
        for idx,node in enumerate(self.depth_first_search(start_node)):
            node_labels[idx] = '(' + str(idx) + ')' + str(node)
            node_categories[idx] = node.__class__.__name__
            idx_dict[node.id] = idx
        for node in self:
            for node2 in node.successors:
                edge_tuple = ( idx_dict[node.id], idx_dict[node2.id] )
                edge_tuples.append(edge_tuple)
        final_text = gml.generate_gml(node_labels,edge_tuples,node_categories)

        if as_string:
            return final_text
        else:
            if filename is None:
                filename = 'rete.gml'

            with open(filename,'w') as f:
                f.write(final_text)
        return None