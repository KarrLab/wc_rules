import networkx as nx
from wc_rules.indexer import Index_By_ID
from utils import AddError, generate_id
import matplotlib.pyplot as plt
import pprint
import operator as op

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

    # Rete net basic operations
    def get_rete_node(self,idx):
        return self.rete_net.node[idx]['data']

    def append_rete_node(self,node):
        self.rete_net.add_node(node.id,data=node)
        return self

    def append_rete_edge(self,node1,node2):
        self.rete_net.add_edge(node1.id,node2.id)
        return self

    def get_rete_successors(self,node):
        x = list(self.rete_net.successors(node.id))
        return [self.get_rete_node(idx) for idx in x]

    def filter_rete_successors(self,node,attr=None,value=None):
        x = self.get_rete_successors(node)
        if (attr,value)==(None,None): return x
        return [z for z in x if getattr(z,attr,None)==value]

    def check_attribute_and_add_successor(self,current_node,_class_to_init,attr=None,value=None):
        # works only for nodes with single argument instantiations
        existing_successors = self.filter_rete_successors(current_node,attr,value)
        if len(existing_successors)==0:
            new_node = _class_to_init(value)
            self.append_rete_node(new_node)
            self.append_rete_edge(current_node,new_node)
            return new_node
        elif len(existing_successors)==1:
            return existing_successors[0]
        else:
            utils.GenericError('Duplicates on the Rete net. Bad!')
        return None

    def draw_rete_net(self):
        labels_dict = dict()
        for n,node in enumerate(self.rete_net.nodes):
            labels_dict[node] = ''.join(['(',str(n),') ',str(self.get_rete_node(node))])
        g1 = nx.relabel_nodes(self.rete_net,labels_dict)
        nx.write_gml(g1, "rete.gml",stringizer=str)
        return self

    # Rete net advanced operations
    def add_checkTYPE_path(self,current_node,type_vec):
        for (kw,_class) in type_vec:
            current_node = self.check_attribute_and_add_successor(current_node,checkTYPE,'_class',_class)
        return current_node

    def add_checkATTR_path(self,current_node,attr_vec):
        new_tuples = sorted([tuple(x[1:]) for x in attr_vec])
        for attr_tuple in new_tuples:
            current_node = self.check_attribute_and_add_successor(current_node,checkATTR,'attr_tuple',attr_tuple)
        return current_node

    def add_storeNODE(self,current_node):
        current_node = self.check_attribute_and_add_successor(current_node,storeNODE)
        return current_node

    def add_aliasNODE(self,current_node,varname):
        current_node = self.check_attribute_and_add_successor(current_node,aliasNODE,'variable_name',varname)
        return current_node

    # Matcher-level operations
    def add_pattern(self,pattern):
        if pattern in self._patterns:
            raise utils.AddError('Multiple patterns with same ID found.')
        self._patterns.append(pattern)
        self.compile_pattern(pattern)

    def compile_pattern(self,pattern):
        qdict = pattern.generate_queries()
        varnames = sorted(qdict['type'].keys())
        new_varnames = { v:str(pattern.id+':'+v) for v in varnames }
        varname_nodes = dict()

        for var in varnames:
            # compile types
            type_vec = qdict['type'][var]
            attr_vec = qdict['attr'][var]
            new_varname = new_varnames[var]
            # for each variable (i.e. each node in the pattern)
            # start from root, add checkTYPE(s), checkATTR(s), store and varname_node
            current_node = self.get_rete_node('root')
            current_node = self.add_checkTYPE_path(current_node,type_vec)
            current_node = self.add_checkATTR_path(current_node,attr_vec)
            current_node = self.add_storeNODE(current_node)
            current_node = self.add_aliasNODE(current_node,new_varname)
            #varname_nodes[new_varname] = current_node

        #edge_stores = []
        #for rel in qdict['rel']:
            #(kw,var1,attr1,attr2,var2) = rel
            #var1_new = new_varnames[var1]
            #var2_new = new_varnames[var2]
            #edge_tuple = (var1_new,attr1,attr2,var2_new)
            #checkedge_node = self.add_checkEDGE(edge_tuple,varname_nodes)
            #storeedge_node = self.add_storeEDGE([var1_new,var2_new],checkedge_node)
            #edge_stores.append(storeedge_node)

        return self

class ReteNode(object):
    def __init__(self,id=None):
        if id is None:
            self.id = generate_id()

class SingleInputNode(ReteNode): pass

class Root(SingleInputNode):
    def __init__(self):
        self.id = 'root'

    def __str__(self):
        return 'root'

class checkTYPE(SingleInputNode):
    def __init__(self,_class,id=None):
        super().__init__(id)
        self._class = _class

    def __str__(self):
        return 'isinstance(*,'+self._class.__name__+')'

class checkATTR(SingleInputNode):
    operator_dict = {
    'lt':'<', 'le':'<=',
    'eq':'==', 'ne':'!=',
    'ge':'>=', 'gt':'>',
    }
    def __init__(self,attr_tuple,id=None):
        super().__init__(id)
        self.attr_tuple = attr_tuple

    def __str__(self):
        attrname = self.attr_tuple[0]
        opname = self.operator_dict[self.attr_tuple[1].__name__]
        value = str(self.attr_tuple[2])
        return ''.join(['*.',attrname,opname,value])

class store(SingleInputNode):
    def __str__(self):
        return 'store'

class storeNODE(store):pass

class aliasNODE(SingleInputNode):
    def __init__(self,name,id=None):
        super().__init__(id)
        self.variable_name = name

    def __str__(self):
        return self.variable_name

class checkEDGE(SingleInputNode):
    def __init__(self,attr1,attr2,id=None):
        super().__init__(id)
        self.attribute_pair = (attr1,attr2)

    def __str__(self):
        return '--'.join(list(self.attribute_pair))

class storeEDGE(store): pass
    
class aliasEDGE(SingleInputNode):
    def __init__(self,name1,name2,id=None):
        super().__init__(id)
        self.variable_names = (name1,name2)

    def __str__(self):
        return self.variable_names


def main():
    from wc_rules.chem import Molecule, Site, Bond
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

    bnd = Bond(id='bnd')
    a1 = A(id='A1').add_sites(X(id='x1',ph=True,v=0).set_bond(bnd))
    a2 = A(id='A2').add_sites(X(id='x2',ph=True,v=1).set_bond(bnd))
    p4 = Pattern('p4').add_node(a1)

    m = Matcher()
    for p in [p4]:
        m.add_pattern(p)
    m.draw_rete_net()


if __name__ == '__main__':
    main()
