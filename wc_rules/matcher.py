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

    # Rete net operations
    def get_rete_node(self,idx):
        return self.rete_net.node[idx]['data']

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

    def draw_rete_net(self):
        labels_dict = dict()
        for n,node in enumerate(self.rete_net.nodes):
            labels_dict[node] = ''.join(['(',str(n),') ',str(self.get_rete_node(node))])
        g1 = nx.relabel_nodes(self.rete_net,labels_dict)
        nx.write_gml(g1, "rete.gml",stringizer=str)
        return self

    # Second-level rete operations
    def add_checkTYPE_path(self,type_vec,current_node):
        for kw, _class in type_vec:
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
        return current_node

    def add_checkATTR_path(self,attr_vec,current_node):
        if len(attr_vec)==0: return current_node
        new_tuples = sorted([tuple(x[1:]) for x in attr_vec])
        for attr_tuple in new_tuples:
            filterby = [('attr_tuple', attr_tuple)]
            existing_nodes = self.get_rete_successors(current_node,filterby=filterby)
            if len(existing_nodes)==0:
                new_node = checkATTR(attr_tuple)
                self.append_rete_node(new_node)
                self.append_rete_edge(current_node,new_node)
                current_node = new_node
            elif len(existing_nodes)==1:
                current_node = existing_nodes[0]
            else:
                raise utils.GenericError('Multiple duplicates found on rete_network. Bad!')
        return current_node

    def add_storeNODE(self,current_node):
        fn = lambda x: isinstance(x,storeNODE)
        existing_nodes = list(filter(fn,self.get_rete_successors(current_node)))
        if len(existing_nodes)==0:
            new_node = storeNODE()
            self.append_rete_node(new_node)
            self.append_rete_edge(current_node,new_node)
            current_node = new_node
        elif len(existing_nodes)==1:
            current_node = existing_nodes[0]
        else:
            raise utils.GenericError('Multiple duplicates found on rete_network. Bad!')
        return current_node

    def add_assignVAR(self,varname,current_node):
        filterby = [('variable_name',varname)]
        existing_nodes = self.get_rete_successors(current_node,filterby=filterby)
        if len(existing_nodes)>0:
            raise utils.GenericError('Name clash detected for pattern variables. Bad!')
        new_node = assignVAR(varname)
        self.append_rete_node(new_node)
        self.append_rete_edge(current_node,new_node)
        current_node = new_node
        return current_node

    def add_checkEDGE(self,edge_tuple,varname_nodes):
        new_node = checkEDGE(edge_tuple)
        (var1,attr1,attr2,var2) = edge_tuple
        var1_node = varname_nodes[var1]
        var2_node = varname_nodes[var2]
        self.append_rete_node(new_node)
        self.append_rete_edge(var1_node,new_node)
        self.append_rete_edge(var2_node,new_node)
        return new_node

    def add_storeEDGE(self,variable_names,checkedge_node):
        new_node = storeEDGE(variable_names)
        self.append_rete_node(new_node)
        self.append_rete_edge(checkedge_node,new_node)
        return new_node

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
            current_node = self.add_checkTYPE_path(type_vec,current_node)
            current_node = self.add_checkATTR_path(attr_vec,current_node)
            current_node = self.add_storeNODE(current_node)
            current_node = self.add_assignVAR(new_varname,current_node)
            varname_nodes[new_varname] = current_node

        edge_stores = []
        for rel in qdict['rel']:
            (kw,var1,attr1,attr2,var2) = rel
            var1_new = new_varnames[var1]
            var2_new = new_varnames[var2]
            edge_tuple = (var1_new,attr1,attr2,var2_new)
            checkedge_node = self.add_checkEDGE(edge_tuple,varname_nodes)
            storeedge_node = self.add_storeEDGE([var1_new,var2_new],checkedge_node)
            edge_stores.append(storeedge_node)

        # to do
        # put edge queries together into a graph query
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
        return 'type '+self._class.__name__

class checkATTR(SingleInputNode):
    def __init__(self,attr_tuple,id=None):
        super().__init__(id)
        self.attr_tuple = attr_tuple

    def __eq__(self,other):
        return super().__eq__(other) and self.attr_tuple == other.attr_tuple

    def __str__(self):
        attrname = self.attr_tuple[0]
        opname = self.attr_tuple[1].__name__
        value = str(self.attr_tuple[2])
        return ' '.join(['attr',attrname,opname,value])

class storeNODE(SingleInputNode):
    def __init__(self,id=None):
        super().__init__(id)

    def __str__(self):
        return 'store'

class assignVAR(SingleInputNode):
    def __init__(self,name,id=None):
        super().__init__(id)
        self.variable_name = name

    def __str__(self):
        return 'var '+self.variable_name

class checkEDGE(object):
    def __init__(self,edge_tuple,id=None):
        if id is None:
            self.id = generate_id()
        else:
            self.id = id
        # edge tuple of the form (var1,attr1,attr2,var2)
        self.edge_tuple = edge_tuple

    def __str__(self):
        (var1,attr1,attr2,var2) = self.edge_tuple
        return ''.join(['edge ',var1,'.',attr1,'--',var2,'.',attr2])

class storeEDGE(SingleInputNode):
    def __init__(self,variable_names,id=None):
        super().__init__(id)
        self.variable_names = variable_names

    def __str__(self):
        return 'store '+','.join(self.variable_names)

class storeCOMBO(object):
    def __init__(self,variable_names,id=None):
        if id is None:
            self.id = generate_id()
        else:
            self.id = id
    def __str__(self):
        return 'store '+','.join(self.variable_names)

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
    a1 = A(id='A1').add_sites(X(id='x1').set_bond(bnd))
    a2 = A(id='A2').add_sites(X(id='x2').set_bond(bnd))
    p4 = Pattern('p4').add_node(a1)

    m = Matcher()
    for p in [p1,p2,p3,p4]:
        m.add_pattern(p)
    m.draw_rete_net()


if __name__ == '__main__':
    main()
