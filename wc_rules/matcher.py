import networkx as nx
from wc_rules.indexer import Index_By_ID, DictSet
from utils import AddError
from palettable.colorbrewer.qualitative import Pastel1_9
import operator as op
from collections import defaultdict
from numpy import argmax
import rete_nodes as rn
import rete_token as rt
import weakref

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
        print([str(x) for x in self])
        return self

    def get_root(self):
        return self['root']

    # Building the rete-net incremenetally
    # the following methods check a node's successors for a particular type of node
    # if found, they return it
    # if not found, they create it, add it as a successor to current node and return it
    def check_attribute_and_add_successor(self,current_node,_class_to_init,attr,value):
        existing_successors = [e for e in current_node.successors if getattr(e,attr,None)==value]
        if len(existing_successors)==0:
            new_node = _class_to_init(value)
            self.add_edge(current_node,new_node)
            return new_node
        elif len(existing_successors)==1:
            return existing_successors[0]
        else:
            utils.GenericError('Duplicates on the Rete net. Bad!')
        return None

    def add_mergenode(self,node1,node2):
        varnames = tuple(sorted(set(node1.variable_names + node2.variable_names)))
        new_node = rn.merge(varnames)
        self.add_edge(node1,new_node)
        self.add_edge(node2,new_node)
        return new_node

    def add_checkTYPE_path(self,current_node,type_vec):
        for (kw,_class) in type_vec:
            current_node = self.check_attribute_and_add_successor(current_node,rn.checkTYPE,'_class',_class)
        return current_node

    def add_checkATTR_path(self,current_node,attr_vec):
        new_tuples = sorted([tuple(x[1:]) for x in attr_vec])
        if len(new_tuples)  > 0:
            current_node = self.check_attribute_and_add_successor(current_node,rn.checkATTR,'tuple_of_attr_tuples',tuple(new_tuples))
        return current_node

    def add_store(self,current_node):
        existing_stores = [x for x in current_node.successors if isinstance(x,rn.store)]
        if len(existing_stores) == 1:
            current_node = existing_stores[0]
        elif len(existing_stores) == 0:
            new_node = rn.store()
            self.add_edge(current_node,new_node)
            current_node = new_node
        else:
            raise utils.GenericError('Duplicates on the Rete net! Bad!')
        return current_node

    def add_aliasNODE(self,current_node,varname):
        var = (varname,)
        current_node = self.check_attribute_and_add_successor(current_node,rn.alias,'variable_names',var)
        return current_node

    def add_checkEDGETYPE(self,current_node,attr1,attr2):
        attrpair = tuple([attr1,attr2])
        current_node = self.check_attribute_and_add_successor(current_node,rn.checkEDGETYPE,'attribute_pair',attrpair)
        return current_node

    def add_aliasEDGE(self,current_node,var1,var2):
        varnames = (var1,var2)
        current_node = self.check_attribute_and_add_successor(current_node,rn.alias,'variable_names',varnames)
        return current_node

    def add_mergenode_path(self,list_of_nodes):
        current_node = list_of_nodes.pop(0)
        for node in list_of_nodes:
            new_node = node
            merge_node = self.add_mergenode(current_node,new_node)
            current_node = merge_node
        return current_node

    def add_aliasPATTERN(self,current_node,name):
        alias_node = rn.alias((name,))
        self.add_edge(current_node,alias_node)
        current_node = alias_node
        return current_node

    ### Drawing the rete-net as a gml
    def draw_as_gml(self,cmap=None,filename=None):
        if not filename:
            filename = 'rete.gml'

        ids_dict = dict()
        for n,node in enumerate(self):
            ids_dict[node.id]=n

        lines = []
        nodecolors = self.get_colors(cmap)
        for n,node in enumerate(self):
            idx = n
            fill = nodecolors[node.__class__.__name__]
            lines.append(self.generate_GML_node(node,idx,fill))
            for elem in node.successors:
                source = idx
                target = ids_dict[elem.id]
                #(source,target) = tuple(ids_dict[x] for x in edge)
                lines.append(self.generate_GML_edge(source,target))

        final_text = self.generate_GML(lines)
        with open(filename,'w') as f:
            f.write(final_text)
        return self

    def get_colors(self,cmap):
        if cmap is None:
            cmap = Pastel1_9
        rete_node_categories = []
        for node in self:
            name = node.__class__.__name__
            if name not in rete_node_categories:
                rete_node_categories.append(name)
        n = len(rete_node_categories)
        x = cmap.hex_colors[:n]
        return dict(zip(rete_node_categories,x))

    def generate_GML_node(self,node,idx,fill):
        label = ''.join(['(',str(idx),') ',str(node)])
        graphics = " graphics [ hasOutline 0 fill \"" + fill + "\" ] "
        labelgraphics = " LabelGraphics [text \"" + label + "\" ] "
        nodetext = "node [id " + str(idx) + graphics + labelgraphics + " ] "
        return nodetext

    def generate_GML_edge(self,source,target):
        st_text = "source " + str(source) + " target " + str(target)
        graphics = " graphics [ fill \"#999999\" targetArrow \"standard\" ] "
        edgetext = "edge [ " + st_text + graphics + " ] "
        return edgetext

    def generate_GML(self,lines):
        graphtext = "graph\n[\n directed 1"
        alltexts = [graphtext] + lines + ["]\n"]
        final_text = '\n'.join(alltexts)
        return final_text

class Matcher(object):
    def __init__(self):
        self.rete_net = ReteNet()

    # Matcher-level operations
    def add_pattern(self,pattern):
        pattern_node = self.compile_pattern(pattern)
        return self

    def compile_pattern(self,pattern):
        ''' Steps through the queries generated by a pattern and increments the Rete net. '''
        qdict = pattern.generate_queries()
        varnames = sorted(qdict['type'].keys())
        new_varnames = { v:str(pattern.id+':'+v) for v in varnames }
        vartuple_nodes = defaultdict(set)

        for var in varnames:
            # compile types
            type_vec = qdict['type'][var]
            attr_vec = qdict['attr'][var]
            new_varname = new_varnames[var]
            # for each variable (i.e. each node in the pattern)
            # start from root, add checkTYPE(s), checkATTR(s), store and varname_node
            current_node = self.rete_net.get_root()
            current_node = self.rete_net.add_checkTYPE_path(current_node,type_vec)
            current_node = self.rete_net.add_checkATTR_path(current_node,attr_vec)
            current_node = self.rete_net.add_store(current_node)
            current_node = self.rete_net.add_aliasNODE(current_node,new_varname)
            vartuple_nodes[(new_varname,)].add(current_node)

        for rel in qdict['rel']:
            (kw,var1,attr1,attr2,var2) = rel
            current_node = self.rete_net.get_root()
            current_node = self.rete_net.add_checkEDGETYPE(current_node,attr1,attr2)
            current_node = self.rete_net.add_store(current_node)
            var1_new = new_varnames[var1]
            var2_new = new_varnames[var2]
            current_node = self.rete_net.add_aliasEDGE(current_node,var1_new,var2_new)
            vartuple_nodes[(var1_new,var2_new)].add(current_node)

        vartuple_nodes2 = dict()
        for vartuple, nodeset in vartuple_nodes.items():
            if len(nodeset) > 1:
                current_node = self.rete_net.add_mergenode_path(sorted(nodeset))
                vartuple_nodes2[vartuple] = current_node
            if len(nodeset) == 1:
                vartuple_nodes2[vartuple] = list(nodeset)[0]

        def sort_tuples(vartuples):
            right = vartuples
            left = []
            flatten_left = set()
            tuple_scorer = lambda x,set1: sum(y in set1 for y in x)
            while len(right) > 0:
                max_index = argmax(list(tuple_scorer(x,flatten_left) for x in right))
                elem = right.pop(max_index)
                left.append(elem)
                for x in elem:
                    flatten_left.add(x)
            return left

        sorted_vartuples = sort_tuples(sorted(vartuple_nodes2))
        sorted_nodes = list(vartuple_nodes2[x] for x in sorted_vartuples)
        current_node = self.rete_net.add_mergenode_path(sorted_nodes)
        current_node = self.rete_net.add_aliasPATTERN(current_node,pattern.id)

        return current_node

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

    p5 = Pattern('p4').add_node( A(id='a3') )
    m = Matcher()
    for p in [p5]:
        m.add_pattern(p)
    m.rete_net.draw_as_gml()

    #tok = rt.ReteToken(id='tok',level=0)
    #print(m.get_rete_node('root').receive_token(tok))


if __name__ == '__main__':
    main()
