from .indexer import DictLike
from .utils import generate_id,ValidateError
from .expr_parse import parse_expression
from .expr2 import parser, Serializer, prune_tree, simplify_tree, BuiltinHook, PatternHook, get_dependencies, build_simple_graph, build_graph_for_symmetry_analysis
from operator import lt,le,eq,ne,ge,gt
import random
import pprint
from collections import deque,defaultdict,namedtuple
from itertools import combinations_with_replacement,combinations

from .rete2 import *

import networkx.algorithms.isomorphism as iso

class Pattern(DictLike):
    def __init__(self,idx,nodelist=None,recurse=True):
        super().__init__()
        self.id = idx
        self._constraints = ''
        self._finalize = False
        self._tree = None
        self._symmetries = None
        self._orbits = None
        #self._nodes = dict()
        if nodelist:
            for node in nodelist:
                self.add_node(node,recurse)

    def get_node(self,idx):
        return self.get(idx)

    def add_node(self,node,recurse=True):
        assert self._finalize is False
        if node not in self:
            self.add(node)
            if recurse:
                for node2 in node.listget_all_related():
                    self.add_node(node2,recurse)
        return self

    @property
    def variable_names(self):
        return [x.id for x in self]
    '''
    def add_expression(self,string_input):
        which_dict,tupl = parse_expression(string_input)
        if tupl is not None:
            if which_dict not in self._expressions:
                self._expressions[which_dict] = set()
            self._expressions[which_dict].add(tupl)
        return self
    '''
    def add_constraints(self,string_input):
        assert self._finalize is False
        strings = [x.strip() for x in string_input.split('\n')]
        strings = [x for x in strings if x not in ['',"\n",None]]
        self._constraints = self._constraints + "\n".join(strings)
        return self

    def validate_dependencies(self,builtin_hook,pattern_hook):
        # checks dependencies internal to the pattern
        if self._tree is None:
            return None

        deps = get_dependencies(self._tree)

        final_deps = defaultdict(set)
        final_deps['variables'] = set([x.id for x in self])

        constants = builtin_hook.allowed_constants
        builtins = builtin_hook.allowed_functions

        for dep in deps:
            # since we're iterating over the dependencies for each constraint,
            # variable assignments prior to using them will be okay
            for var in sorted(dep['variables']):
                # is the variable already in the pattern
                if var not in final_deps['variables'] | final_deps['assignments'] | constants:
                    raise ValidateError('Variable ' + var + ' not found in pattern ' + self.id)
            for var,attr in sorted(dep['attributes']):
                # is the attribute present on the variable
                # can only be checked for non-assigned variables
                if var in final_deps['variables']:
                    if attr not in self[var].get_literal_attributes():
                        raise ValidateError('Attribute ' + attr + ' not found in variable ' + var)
            for var, fname, kws in sorted(dep['varmethods']):
                # is the function available to the variable
                if var in final_deps['variables']:
                    fns_dict = self[var].get_dynamic_methods()
                    if fname not in fns_dict:
                        raise ValidateError('Method ' + fname + ' not found in variable ' + var)
                    fn = fns_dict[fname]
                    # are the keywords correct
                    if kws is not None:
                        for kw in kws:
                            if kw not in fn._vars:
                                raise ValidateError('Keyword ' + kw + ' not found in method ' + var + '.' + fname)
            for var in dep['assignments']:
                # are assigned variables uniquely assigned and different from existing variables
                if var in final_deps['variables'] | final_deps['assignments']:
                    raise ValidateError('New variable ' + var + ' cannot clash with existing variables ')
                final_deps['assignments'].add(var)
            for fn in dep['builtins']:
                # are the builtin functions used allowed ones
                if fn not in builtins:
                    raise ValidateError('Builtin function ' + fn + ' not found')
            for pat,vpairlist in dep['patternvarpairs']:
                pvars = []
                for pvar,var in vpairlist:
                    if var not in final_deps['variables']:
                        raise ValidateError('Variable ' + var + ' not found in pattern ' + self.id)
                    pvars.append(pvar)
                final_deps['patternvars'].add(tuple([pat,tuple(pvars)]))
            for fn in dep['matchfuncs']:
                if fn not in pattern_hook.allowed_methods:
                    raise ValidateError('The method ' + fn + ' is not available to match objects')
        return deps

    def validate_pattern_connectivity(self):
        # ensure there are no neighbour nodes not in pattern
        examined = set()
        self._adjacent = dict()
        
        start_node = self[min(self._dict.keys())]
        stack = deque([start_node])        
        while len(stack)>0:
            current_node = stack.popleft()
            all_related = current_node.listget_all_related()
            self._adjacent[current_node.id] = [x.id for x in all_related]
            assert current_node in self
            next_neighbours = set(all_related) - examined
            examined.add(current_node)
            stack.extendleft(list(next_neighbours))

        # ensure pattern is fully connected
        assert sorted([x.id for x in examined])==sorted(self.keys())
        return self

    def process_direct_constraints(self):
        strings = []
        for node in self:
            for attr in node.get_nonempty_scalar_attributes():
                val = getattr(node,attr)
                if isinstance(val,str):
                    val = '"' + val + '"'
                else:
                    val = str(val)
                strings.append(node.id + '.' + attr + ' == ' + val)
        return "\n".join(strings)

    def parse_constraints(self):
        # direct constraints: attribute constraints set directly, e.g., A('a',ph=True)
        # self._constraints: constraints set using add_constraints(), e.g., A('a').add_constraints('''a.ph==True''')
        direct_constraints = self.process_direct_constraints()
        additional_constraints = self._constraints
        
        if direct_constraints == '' and additional_constraints == '':
            return None

        total_constraint_string = "\n".join([self.process_direct_constraints(),self._constraints])
        tree = parser.parse(total_constraint_string)
        tree = prune_tree(tree)
        modified = True
        while modified:
            tree,modified = simplify_tree(tree)
        return tree

    def compute_internal_morphisms(self,G):

        def nodematch(x,y):
            return x['data'].category == y['data'].category and x['data'].matching == y['data'].matching

        def edgematch(x,y):
            return x['label'] == y['label']
        
        morphisms = list(iso.DiGraphMatcher(G,G,nodematch,edgematch).isomorphisms_iter())
        return morphisms

    def compute_symmetries(self,g):
                
        def nodematch(x,y):
            v = x['data'].category == y['data'].category and x['data'].matching == y['data'].matching
            return v

        def edgematch(x,y):
            v =  x['label'] == y['label']
            return v
        
        def compute_internal_morphisms(g):
            return iso.DiGraphMatcher(g,g,nodematch,edgematch).isomorphisms_iter()

        def retrieve_name(g,x):
            return g.nodes[x]['data'].name

        def retrieve_mapping(g,m,names):
            d = [(retrieve_name(g,x),retrieve_name(g,y)) for x,y in m.items() if retrieve_name(g,x) in names]
            return tuple(sorted(d))

        symmetries = sorted(set([retrieve_mapping(g,m,self.variable_names) for m in compute_internal_morphisms(g)]))
        return symmetries

    def analyze_symmetries(self,deps):
        # scaffold: set of nodes, edges, nodetypes and edgetypes
        # full pattern: scaffold + constraints
        
        g,node_dict,counter = build_simple_graph(self)
        g,node_dict = build_graph_for_symmetry_analysis(g,node_dict,counter,deps,self._tree)
        final_symmetries = self.compute_symmetries(g)
        return [{x:y for x,y in m} for m in final_symmetries]
        
        
    def analyze_orbits(self):
        orbits = {x:set([x]) for x in self.variable_names}
        for m in self._symmetries:
            for x,y in m.items():
                if x!=y:
                    orbits[x].add(y)
                    orbits[y].add(x)
        return set([frozenset(orbits[x]) for x in self.variable_names])
       
    def print_graph(self,G):
        for node in G.nodes(data=True):
            print(node)
        for edge in G.edges(data=True):
            print(edge)
        #print(pprint.pformat(node_dict))
        return

    def finalize(self,builtin_hook=BuiltinHook(),pattern_hook=PatternHook()): 
        self.validate_pattern_connectivity()
        self._tree = self.parse_constraints()
        deps = self.validate_dependencies(builtin_hook,pattern_hook)
        self._symmetries = self.analyze_symmetries(deps)
        self._orbits = self.analyze_orbits()
        self.build_rete_subset()
        return self

    def remove_node(self,node):
        return self.remove(node)

    def __str__(self):
        return 'Pattern id ' + self.id + ' with ' + super().__str__()

    def duplicate(self,idx=None,preserve_ids=False):
        if idx is None:
            idx = generate_id()
        new_pattern = self.__class__(idx)
        nodemap = dict()
        for node in self:
            # this duplicates upto scalar attributes
            new_node = node.duplicate(preserve_id=preserve_ids)
            nodemap[node.id] = new_node
            new_pattern.add_node(new_node,recurse=False)
        for node in self:
            # this duplicates related attributes given nodemap
            new_node = nodemap[node.id]
            node.duplicate_relations(new_node,nodemap)
        return new_pattern

    def duplicate_with_keymap(self,idx,keymap=None):
        if keymap is None:
            keymap = {x.id:x.id for x in self}
        new_pattern = self.__class__(idx)
        nodemap = dict()
        for node in self:
            new_node = node.duplicate(id=keymap[node.id])
            new_pattern.add_node(new_node,recurse=False)
            nodemap[node.id] = new_node
        for node in self:
            new_node = nodemap[node.id]
            node.duplicate_relations(new_node,nodemap)
        return new_pattern


    #### building rete subset
    def get_classtuple_paths(self):
        # classtuples {node.id: (class,class,class,Entity)}
        ClassTuple = namedtuple("ClassTuple",["cls"])
        classtuples = dict()
        for node in self:
            path = deque()
            for _class in node.__class__.__mro__:
                if _class.__name__ == 'BaseClass':
                    break
                path.appendleft(ClassTuple(cls=_class))
            classtuples[node.id] = path
        return classtuples

    def get_edgetuples(self):
        # edgetuples {(node1.id,node2.id): [(class1,attr1,attr2,class2),...]}
        # where attr1 < attr2
        edgetuples = dict()
        visited = set()
        EdgeTuple = namedtuple("EdgeTuple",["cls1","attr1","attr2","cls2"])
        start = self[sorted([x.id for x in self])[0]]
        next_node = deque([start])
        while next_node:
            node = next_node.popleft()
            for attr in node.get_nonempty_related_attributes():
                related_attr = node.get_related_name(attr)
                neighbours = [n for n in node.listget(attr) if n not in visited]
                next_node.extend(neighbours)
                for n in neighbours:
                    if attr < related_attr:
                        tup = EdgeTuple(cls1=node.__class__,attr1=attr,attr2=related_attr,cls2=n.__class__)
                        key = (node.id,n.id)
                    else:
                        tup = EdgeTuple(cls1=n.__class__,attr1=related_attr,attr2=attr,cls2=node.__class__)
                        key = (n.id,node.id)
                    if key not in edgetuples:
                        edgetuples[key] = deque()
                    edgetuples[key].append(tup)
            visited.add(node)
        return edgetuples

    def get_optimal_merge_path(self,edgetuples,verbose=False):
        # return a sequence of nodes
        def populate_connectivity_scores(varnames,edgetuples):
            n = len(varnames)
            connectivity_scores = defaultdict(lambda:dict(zip(varnames,[0]*n)))
            for (idx1,idx2),edgedeque in edgetuples.items():
                connectivity_scores[idx1][idx2] += len(edgedeque)
                connectivity_scores[idx2][idx1] += len(edgedeque)
            return connectivity_scores

        def populate_symmetry_scores(varnames,orbits):
            n = len(varnames)
            symmetry_scores = defaultdict(lambda:dict(zip(varnames,[1]*n)))
            for orbit in orbits:
                for i,j in combinations(orbit,2):
                    symmetry_scores[i][j] += 1
                    symmetry_scores[j][i] += 1
            return symmetry_scores

        def sum_over(x,scores,somelist):
            if len(somelist)==0:
                return 0
            return sum([scores[x][y] for y in somelist])

        def score_function(x,merged,connectivity_scores,symmetry_scores):
            s1 = sum_over(x,connectivity_scores,merged)
            s2 = sum_over(x,symmetry_scores,merged)
            s3 = x
            return (-s1*s2,s3)
    

        connectivity_scores = populate_connectivity_scores(self.variable_names,edgetuples)
        symmetry_scores = populate_symmetry_scores(self.variable_names,self._orbits)        

        unmerged = self.variable_names.copy()
        merged = deque()
        score = dict()
            
        while unmerged:
            score = {x:score_function(x,merged,connectivity_scores,symmetry_scores) for x in unmerged}
            unmerged = sorted(unmerged,key=lambda x:score[x])
            merged.append(unmerged.pop(0))
            if verbose:
                pprint.pprint(score)
                print('Unmerged: ', unmerged)
                print('Merged: ', merged)
                print()
        return merged

    def build_rete_subset(self):
        # classtuples {node.id: (class,class,class,Entity)}
        # edgetuples {(node1.id,node2.id): [(class1,attr1,attr2,class2),...]}, where attr1 < attr2
        classtuples = self.get_classtuple_paths()
        edgetuples = self.get_edgetuples()
        unmerged = self.get_optimal_merge_path(edgetuples,verbose=False)
        merged = deque()

        mergetuples = deque()
        left_index = dict()
        right_index = dict()
        print(unmerged)
        while unmerged:
            candidate = unmerged.popleft()
            if len(merged)==0:
                print(candidate)
                merged.append(candidate)
                continue
            edges_with_candidate_at_index_0 = [e for (n1,n2),elist in edgetuples.items() for e in elist if n1==candidate and n2 in merged]
            edges_with_candidate_at_index_3 = [e for (n1,n2),elist in edgetuples.items() for e in elist if n2==candidate and n1 in merged]
            edges = edges_with_candidate_at_index_0 + edges_with_candidate_at_index_0
            print(candidate)
            print(edges)
            print()

            merged.append(candidate)

        #for (n1,n2),elist in edgetuples.items():
        #    print(n1,n2,elist)
            




        #pprint.pprint(merged)
        MergeTuple = namedtuple("MergeTuple",['lhs','rhs','remap'])
        mergetuples = set()
        return self

    """
    def generate_queries_TYPE(self):
        ''' Generates tuples ('type',_class) '''
        type_queries = {}
        for node in self:
            idx = node.id
            type_queries[idx] = []
            list_of_classes = node.__class__.__mro__
            for _class in reversed(list_of_classes):
                if _class.__name__ in ['BaseClass','Model','object']:
                    continue
                v = ['type',_class]
                type_queries[idx].append(tuple(v))
        return type_queries

    def generate_queries_ATTR(self):
        ''' Generates tuples ('attr',attrname,operator,value) '''
        attr_queries = {}
        for node in self:
            idx = node.id
            attr_queries[idx] = []
            for attr in sorted(node.get_nonempty_scalar_attributes()):
                if attr=='id': continue
                v = ['attr',attr,eq,getattr(node,attr)]
                attr_queries[idx].append(tuple(v))

        op_str = ['<','<=','==','!=','>=','>']
        ops = [lt,le,eq,ne,ge,gt]
        op_dict = dict(zip(op_str,ops))
        if 'bool_cmp' in self._expressions:
            for entry in self._expressions['bool_cmp']:
                var,attr,op,value = entry
                v = ['attr',attr,op_dict[op],value]
                attr_queries[var].append(tuple(v))
        if 'num_cmp' in self._expressions:
            for entry in self._expressions['num_cmp']:
                var,attr,op,value = entry
                v = ['attr',attr,op_dict[op],value]
                attr_queries[var].append(tuple(v))
        return attr_queries

    def generate_queries_REL(self):
        ''' Generate tuples ('rel',idx1,attrname,related_attrname,idx2) '''
        rel_queries = []
        already_encountered = []
        for node in self:
            idx = node.id
            for attr in node.get_nonempty_related_attributes():
                for node2 in node.listget(attr):
                    if node2.id in already_encountered:
                        continue
                    related_attr = node.__class__.Meta.local_attributes[attr].related_name
                    # this is alphabetical comparison 'ab' < 'b'
                    if attr <= related_attr:
                            v = ['rel',idx,attr,related_attr,node2.id]
                    else:
                        v = ['rel',node2.id,related_attr,attr,idx]
                    rel_queries.append(tuple(v))
            already_encountered.append(idx)

        if 'is_empty' in self._expressions:
            varlist = self._expressions['is_empty']
            for (var,attr) in varlist:
                node  = self.get_node(var)
                related_attr = node.__class__.Meta.local_attributes[attr].related_name
                if attr < related_attr:
                    v = ['rel',var,attr,related_attr,None]
                else:
                    v = ['rel',None,related_attr,attr,var]
                rel_queries.append(tuple(v))
        return rel_queries

    def generate_queries_ISIN(self):
        is_in = []
        if 'is_in' in self._expressions:
            is_in = [('is_in',x) for x in self._expressions['is_in']]
        return is_in

    def generate_queries_ISNOTIN(self):
        is_not_in = []
        if 'is_not_in' in self._expressions:
            is_not_in = [('is_not_in',x) for x in self._expressions['is_not_in']]
        return is_not_in

    def generate_queries(self):
        return {
            'type': self.generate_queries_TYPE(),
            'attr': self.generate_queries_ATTR(),
            'rel': self.generate_queries_REL(),
            'is_in': self.generate_queries_ISIN(),
            'is_not_in': self.generate_queries_ISNOTIN(),
        }
    """
def main():
    pass


if __name__ == '__main__':
    main()
