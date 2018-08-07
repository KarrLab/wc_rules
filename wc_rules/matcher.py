import networkx as nx
from wc_rules.indexer import Index_By_ID
from utils import AddError, generate_id
import matplotlib.pyplot as plt
import pprint

class Token(dict):
    ''' Each token is a dict whose keys are pattern node ids
    and values are wmg node ids '''

    def __init__(self,**kwargs):
        self['tag'] = kwargs.pop('tag')
        self['species'] = kwargs.pop('species')
        for kwarg in kwargs:
            self[kwarg] = kwargs[kwarg]


class Matcher(object):
    def __init__(self):
        self.rete_net = nx.DiGraph()
        self.rete_net.add_node('root', data=Root())
        self._patterns = Index_By_ID()

    def add_pattern(self,pattern):
        if pattern in self._patterns:
            raise utils.AddError('Multiple patterns with same ID found.')
        self._patterns.append(pattern)
        self.compile_pattern(pattern)

    def append_rete_node(self,node):
        self.rete_net.add_node(node.id,data=node)
        return self

    def append_rete_edge(self,node1,node2):
        self.rete_net.add_edge(node1.id,node2.id)
        return self

    def get_rete_successors(self,node,filterby=None):
        successors = list(self.rete_net.successors(node.id))
        if filterby is not None:
            # filterby should be a list of attr_value_tuples
            new_list = []
            for elem in successors:
                valid = True
                for (attr,value) in filterby:
                    if getattr(self.get_rete_node(elem),attr,None) != value:
                        valid = False
                        break
                if valid:
                    new_list.append(elem)
        else:
            new_list = successors
        return [self.get_rete_node(idx) for idx in new_list]

    def get_rete_node(self,idx):
        return self.rete_net.node[idx]['data']

    def compile_pattern(self,pattern):
        qdict = pattern.generate_queries()
        # first get the varnames, i.e., pattern nodenames
        varnames = sorted(qdict['type'].keys())
        new_varnames = { (v,str(pattern.id+'.'+v)) for v in varnames }

        type_dict = qdict['type']
        for var in varnames:
            # compile types
            current_node = self.get_rete_node('root')
            for kw,_class in type_dict[var]:
                filterby = [('_class',_class)]
                existing_nodes = self.get_rete_successors(current_node,filterby=filterby)
                if len(existing_nodes)==0:
                    new_node = checkTYPE(_class)
                    self.append_rete_node(new_node)
                    self.append_rete_edge(current_node,new_node)
                    current_node = new_node
                elif len(existing_nodes)==1:
                    current_node = existing_nodes[0]
                else:
                    raise utils.GenericError('Multiple duplicates found on rete_network. Bad!')
        return self

    def draw_rete_net(self):
        labels_dict = dict()
        for n,node in enumerate(self.rete_net.nodes):
            labels_dict[node] = ''.join(['(',str(n),') ',str(self.get_rete_node(node))])
        g1 = nx.relabel_nodes(self.rete_net,labels_dict)
        nx.write_gml(g1, "rete.gml",stringizer=str)
        return self



class SingleInputNode(object):
    def __init__(self,id=None):
        if id is None:
            self.id = generate_id()

    def __eq__(self,other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash(self.id)

class Root(SingleInputNode):
    def __init__(self):
        self.id = 'root'

    def __str__(self):
        return 'root'

class checkTYPE(SingleInputNode):
    def __init__(self,_class,id=None):
        super().__init__(id)
        self._class = _class

    def __eq__(self,other):
        return super().__eq__(other) and self._class.__name__ == other._class.__name__

    def __str__(self):
        return 'is type '+self._class.__name__

def main():
    from wc_rules.chem import Molecule, Site
    from wc_rules.pattern import Pattern
    from wc_rules.species import Species
    from obj_model import core

    class A(Molecule):pass
    class X(Site):
        ph = core.BooleanAttribute(default=None)
        v = core.IntegerAttribute(default=None)

    p1 = Pattern('p1').add_node( A(id='A').add_sites(X(id='x',ph=True,v=0)) )
    p2 = Pattern('p2').add_node( A(id='A').add_sites(X(id='x',ph=True)) )
    p3 = Pattern('p3').add_node( A(id='A').add_sites(X(id='x')) )

    m = Matcher()
    for p in [p1,p2,p3]:
        m.add_pattern(p)
    m.draw_rete_net()


if __name__ == '__main__':
    main()
