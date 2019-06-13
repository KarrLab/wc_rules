from .indexer import DictLike
from .utils import generate_id,ValidateError
from .expr_parse import parse_expression
from .expr2 import parser, Serializer, prune_tree, simplify_tree, BuiltinHook, PatternHook, get_dependencies, build_simple_graph, build_graph_for_symmetry_analysis
from operator import lt,le,eq,ne,ge,gt
import random
import pprint
from collections import deque,defaultdict,namedtuple
from itertools import combinations_with_replacement,combinations
import inspect

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

    def compute_orbits(self,symmetries):
        orbits = {x:set([x]) for x in self.variable_names}
        for m in symmetries:
            for x,y in m:
                if x!=y:
                    orbits[x].add(y)
                    orbits[y].add(x) 
        return set([frozenset(orbits[x]) for x in self.variable_names])

    def analyze_symmetries(self):
        # scaffold: set of nodes, edges, nodetypes and edgetypes
        # full pattern: scaffold + constraints
        
        g,node_dict,counter = build_simple_graph(self)
        scaffold_symmetries = self.compute_symmetries(g)

        g,node_dict = build_graph_for_symmetry_analysis(g,node_dict,counter,self._deps,self._tree)
        final_symmetries = self.compute_symmetries(g)
        return scaffold_symmetries,final_symmetries
            
    def analyze_orbits(self):
        return self.compute_orbits(self._scaffold_symmetries), self.compute_orbits(self._final_symmetries)
        
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
        self._deps = self.validate_dependencies(builtin_hook,pattern_hook)
        self._scaffold_symmetries, self._final_symmetries = self.analyze_symmetries()
        self._scaffold_orbits, self._final_orbits = self.analyze_orbits()
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
        
        def get_total_connectivity_scores(edgetuples):
            total_connectivity = defaultdict(int)
            for (idx1,idx2), edgedeque in edgetuples.items():
                total_connectivity[idx1] += len(edgedeque)
                total_connectivity[idx2] += len(edgedeque)
            return total_connectivity

        def get_local_connectivity_scores(edgetuples):
            local_connectivity = defaultdict(lambda:defaultdict(int))
            for (idx1,idx2), edgedeque in edgetuples.items():
                local_connectivity[idx1][idx2] += len(edgedeque)
                local_connectivity[idx2][idx1] += len(edgedeque)
            return local_connectivity

        def get_total_symmetry_scores(orbits):
            total_symmetry_score = defaultdict(int)
            for orbit in orbits:
                for idx in orbit:
                    total_symmetry_score[idx] = len(orbit)
            return total_symmetry_score

        def get_local_symmetry_scores(orbits):
            local_symmetry_score = defaultdict(lambda:defaultdict(int))
            for orbit in orbits:
                for idx1,idx2 in combinations(orbit,2):
                    local_symmetry_score[idx1][idx2] += 1
                    local_symmetry_score[idx2][idx1] += 1
            return local_symmetry_score

        def sum_over(x,local_scores,merged):
            return sum([local_scores[y] for y in merged])

        def score_fn(x,scoredict,merged):
            # low local symmetry
            # low total symmetry
            # high local connectivity
            # high total connectivity
            # low label

            s1 = sum_over(x,scoredict['local_symmetry'][x],merged)
            s2 = scoredict['total_symmetry'][x]
            s3 = - sum_over(x,scoredict['local_connectivity'][x],merged)
            s4 = - scoredict['total_connectivity'][x]
            return (s1,s2,s3,s4,x)


        # compute local and total scores 
        scoredict = {
        'total_connectivity': get_total_connectivity_scores(edgetuples),
        'local_connectivity': get_local_connectivity_scores(edgetuples),
        'total_symmetry': get_total_symmetry_scores(self._scaffold_orbits),
        'local_symmetry': get_local_symmetry_scores(self._scaffold_orbits),
        }

        #pprint.pprint(scoredict)

        # merging happens here
        unmerged = self.variable_names.copy()
        merged = deque()
        score = dict()
        
        while unmerged:
            score = {x:score_fn(x,scoredict,merged) for x in unmerged}
            if verbose:
                pprint.pprint(score)
            unmerged = sorted(unmerged,key=lambda x:score[x])
            merged.append(unmerged.pop(0))
            if verbose:
                print('Unmerged: ', unmerged)
                print('Merged: ', merged)
                print()
        
        return merged
        

    def build_merge_sequence(self,classtuples,edgetuples,mergepath):
        def edgetuple_iter(edges,path):
            i=-1
            for n1,n2 in sorted(edges.keys(),key=lambda x: (min(path.index(x[0]),path.index(x[1])),x[0],x[1]) ):
                for e in sorted(edges[(n1,n2)]):
                    i += 1
                    yield (i,n1,n2,e)

        def remap_func(nodes,path):
            return tuple([(path.index(x),nodes.index(x)) for x in nodes])

        def redo_symmetries(symmetries,path):
            return [tuple(sorted([(path.index(x),path.index(y)) for x,y in sym])) for sym in symmetries]
            
        def compute_subgraph_symmetries_by_level(symmetries,path):
            # an n-level is a subgraph  composed from first n nodes of path
            # redo symmetries from labels to mergepath indices            
            syms = [tuple(sorted([(path.index(x),path.index(y)) for x,y in sym])) for sym in symmetries]
            leveldict = {}
            for level in range(0,len(path)):
                level_syms = set()
                for sym in syms:
                    # subset of symmetry map for that level 
                    current_sym = [(x,y) for x,y in sym if x<=level and y<=level]
                    # is the subset itself a symmetry (size = level+1)
                    if len(current_sym) == level + 1:
                        level_syms.add(tuple(current_sym))
                leveldict[level] = sorted(level_syms)[1:]
                # here, we skip the identity symmetry

            # now we go through leveldict and remove symmetries whose subsets
            # were already checked at a previous level
            for level in range(0,len(path)-1):
                current_level_syms = leveldict[level]
                #print(current_level_syms)
                for level2 in range(level+1,len(path)):
                    higher_level_syms = leveldict[level2]
                    new_syms = []
                    for sym in higher_level_syms:
                        exclude = False
                        for old_sym in current_level_syms:
                            if old_sym==sym[:level+1]:
                                exclude = True
                        if not exclude:
                            new_syms.append(sym)
                    if len(new_syms) < len(higher_level_syms):
                        leveldict[level2] = new_syms
            return leveldict
        
        # computing subgraph symmetries to be checked
        # {level: [sym,]}
        leveldict = compute_subgraph_symmetries_by_level(self._scaffold_symmetries,mergepath)
        #pprint.pprint(leveldict)

        # populate mergetuples
        # Assumptions: rete-node that processes an edge (class(n1),attr1,attr2,class(n2)) will store/output a token (n1,n2)
        MergeTuple = namedtuple("MergeTuple",[
            'lhs','rhs',
            'lhs_remap','rhs_remap',
            'token_length',
            'check_symmetries'])
        mergetuples = deque()
        if len(edgetuples)==0:
            # case 1: pattern has only one node
            var = list(classtuples.keys())[0]
            new_merge_node = MergeTuple(
                lhs=classtuples[var][-1],
                lhs_remap=tuple([(0,0)]),
                rhs=None,
                rhs_remap=None,
                token_length=1,
                check_symmetries = None
                )
            mergetuples.append(new_merge_node)
        elif len(edgetuples)==1:
            # case 2: pattern has only one edge
            new_merge_node = MergeTuple(
                lhs=edgetuples[0],
                rhs=None,
                lhs_remap=lhs_remap,
                rhs_remap=None,
                token_length=2,
                check_symmetries = None
                )
            mergetuples.append(new_merge_node)
        else:
            # case 3: pattern has more than one edge
            for i,n1,n2,e in edgetuple_iter(edgetuples,mergepath):
                if i==0:
                    # set seed lhs
                    lhs = e
                    lhs_nodes = [n1,n2]
                    lhs_remap = remap_func(lhs_nodes,mergepath)
                    continue

                # set every successive rhs
                rhs = e
                rhs_nodes = [n1,n2]
                rhs_remap = remap_func(rhs_nodes,mergepath)
                merged_nodes = [x for x in mergepath if x in lhs_nodes or x in rhs_nodes]
                newly_added_nodes = [x for x in rhs_nodes if x not in lhs_nodes]
                if len(newly_added_nodes) > 0 and len(merged_nodes)>1 and leveldict[len(merged_nodes)-1] != []:
                    check_symmetries = tuple(leveldict[len(merged_nodes)-1])
                else:
                    check_symmetries = None
                
                new_merge_node = MergeTuple(
                        lhs=lhs,
                        rhs=rhs,
                        lhs_remap=lhs_remap,
                        rhs_remap=rhs_remap,
                        token_length=len(merged_nodes),
                        check_symmetries=check_symmetries
                        )
                mergetuples.append(new_merge_node)

                lhs = new_merge_node
                lhs_nodes = merged_nodes
                lhs_remap = remap_func(lhs_nodes,mergepath)
        
        #### TODO
        #### Segregate original symmetry maps into 
        #### ones preserved by final pattern vs not preserved
        #### now, add generators for the broken symmetries onto the scaffold
        
        return mergetuples

    def get_attrtuples(self):
        simple_attribute_calls = set.union(*[dep['attributes'] for dep in self._deps]) 
        dynamic_attribute_calls = set()
        varmethods_to_check = set.union(*[dep['varmethods'] for dep in self._deps])
        for var,varmethod,kws in varmethods_to_check:
            arguments = self[var].get_dynamic_methods()[varmethod]._args
            attrs = self[var].get_literal_attrs()
            attrdeps = [x for x in arguments if x in attrs]
            for x in attrdeps:
                dynamic_attribute_calls.add( (var,x,))
        AttrTuple = namedtuple("AttrTuple",['cls','attr'])
        attrtuples = dict()
        for var,attr in (simple_attribute_calls|dynamic_attribute_calls):
            _cls =self[var].__class__
            if var not in attrtuples:
                attrtuples[var] = deque()
            a = AttrTuple(cls=_cls,attr=attr)
            attrtuples[var].append(a)

        for var in attrtuples:
            attrtuples[var] = tuple(sorted(attrtuples[var]))
            
        return attrtuples
        
    def build_rete_subset(self):
        # classtuples {node.id: (class,class,class,Entity)}
        # edgetuples {(node1.id,node2.id): [(class1,attr1,attr2,class2),...]}, where attr1 < attr2
        # mergetuples [ MergeTuple(lhs=merge/edge tuple,rhs=...,
        #                          lhs_remap=[(path.index,lhs_nodes.index),rhs_remap=...],
        #                          token_length=n,prune_symmetries=[...]) ]
        # attrtuples { node.id: (class,var) }
        classtuples = self.get_classtuple_paths()
        edgetuples = self.get_edgetuples()
        mergepath = self.get_optimal_merge_path(edgetuples,verbose=False)
        mergetuples = self.build_merge_sequence(classtuples,edgetuples,mergepath)
        #attrtuples = self.get_attrtuples()

        # get set of classtuples 
        classtuple_set = set()
        [classtuple_set.update(x) for x in classtuples.values()]
        #pprint.pprint(classtuple_set)
        
        # get set of edgetuples
        edgetuple_set = set()
        [edgetuple_set.update(x) for x in edgetuples.values()]
        #pprint.pprint(edgetuple_set)
        
        #for m in mergetuples:
        #    print(m)
        
        return self

        #patterntuple = self.make_patterntuple(mergepath,mergetuples[-1],attrtuples)
        #return (classtuples,edgetuples,mergetuples,attrtuples,patterntuple)

        
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
