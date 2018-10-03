from indexer import DictSet
from utils import AddError
import rete_nodes as rn
import rete_build as rb
import gml

import operator as op
from collections import deque

class ReteNet(DictSet):
    def __init__(self):
        super().__init__([rn.Root()])

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

    def draw_as_gml(self,filename=None):
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
        if not filename:
            filename = 'rete.gml'
        final_text = gml.generate_gml(node_labels,edge_tuples,node_categories)
        with open(filename,'w') as f:
            f.write(final_text)
        return self

class Matcher(object):
    def __init__(self):
        self.rete_net = ReteNet()

    # Matcher-level operations
    def add_pattern(self,pattern):
        rb.increment_net_with_pattern(self.rete_net,pattern)
        return self

def main():
    from wc_rules.chem import Molecule, Site, Bond
    from wc_rules.pattern import Pattern
    from obj_model import core

    class A(Molecule):pass
    class X(Site):
        ph = core.BooleanAttribute(default=None)
        v = core.IntegerAttribute(default=None)

    p1 = Pattern('p1').add_node( A(id='A').add_sites(X(id='x',ph=True,v=0)) )
    p2 = Pattern('p2').add_node( A(id='A').add_sites(X(id='x',ph=True)) )
    p3 = Pattern('p3').add_node( A(id='A').add_sites(X(id='x')) )

    bnd = Bond(id='bnd')
    a1 = A(id='A1').add_sites(X(id='x1',ph=True,v=0).set_bond(bnd))
    a2 = A(id='A2').add_sites(X(id='x2',ph=True,v=1).set_bond(bnd))
    p4 = Pattern('p4').add_node(a1)

    p5 = Pattern('p5').add_node( A(id='a3') )
    m = Matcher()
    for p in [p1,p2,p3,p4,p5]:
        m.add_pattern(p)
    m.rete_net.draw_as_gml()

    #tok = rt.ReteToken(id='tok',level=0)
    #print(m.get_rete_node('root').receive_token(tok))


if __name__ == '__main__':
    main()
