from .indexer import DictLike
from .utils import generate_id,ValidateError
from .expr_parse import parse_expression
from .expr2 import parser, Serializer, prune_tree, simplify_tree, BuiltinHook, PatternHook, get_dependencies, build_simple_graph, build_graph_for_symmetry_analysis
from operator import lt,le,eq,ne,ge,gt,xor
import random
import pprint
from collections import deque,defaultdict,namedtuple
from itertools import combinations_with_replacement,combinations
import bisect
import inspect
from sortedcontainers import SortedSet


from .rete2 import *

import networkx.algorithms.isomorphism as iso

class Pattern(DictLike):
    def __init__(self,idx,nodelist=None,recurse=True):
        super().__init__()
        self.id = idx
        self._constraints = ''
        self._finalized = False
        self._tree = None
        self._deps = None
        self._scaffold_symmetries = None
        self._scaffold_orbits = None
        self._final_symmetries = None
        self._final_orbits = None
        
        #self._nodes = dict()
        if nodelist:
            for node in nodelist:
                self.add_node(node,recurse)

    def get_node(self,idx):
        return self.get(idx)

    def add_node(self,node,recurse=True):
        assert self._finalized is False, "Pattern already in use. Cannot be modified."
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
        assert self._finalized is False, "Pattern already in use. Cannot be modified."
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
                            if kw not in fn._args:
                                raise ValidateError('Keyword argument ' + kw + ' not found in method ' + var + '.' + fname)
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
        self._finalized = True
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
    def get_edgetuples(self):
        # edgetuples {(node1.id,node2.id): [(class1,attr1,attr2,class2),...]}
        # where attr1 < attr2
        edgetuples,edgetuple_set = dict(),set()
        visited = set()
        EdgeTuple = namedtuple("EdgeTuple",["cls1","attr1","attr2","cls2"])
        start = self[sorted([x.id for x in self])[0]]
        next_node = deque([start])
        while next_node:
            node = next_node.popleft()
            visited.add(node)
            for attr in node.get_nonempty_related_attributes():
                related_attr = node.get_related_name(attr)
                neighbours = [n for n in node.listget(attr) if n not in visited]
                next_node.extend(neighbours)
                for n in neighbours:
                    (attr1,cls1,idx1),(attr2,cls2,idx2) = sorted([(attr,node.__class__,node.id),(related_attr,n.__class__,n.id)])
                    tup = EdgeTuple(cls1=cls1,attr1=attr1,attr2=attr2,cls2=cls2)
                    key = (idx1,idx2)
                    if key not in edgetuples:
                        edgetuples[key] = deque()
                    edgetuples[key].append(tup)
                    edgetuple_set.add(tup)
        return edgetuples,edgetuple_set
  
    def sort_orbits(self,edgetuples):
        orbits = self._scaffold_orbits
        # orbits sorted by external degree, internal degree, orbit size, node class, and
        # as a worst case scenario, lowest id
        orbsortkeys = dict()
        for orb in orbits:
            orbsize = len(orb)
            rep = min(orb)
            classname = rep.__class__.__name__
            selected_tuples = [(x,y) for (x,y) in edgetuples.keys() if x==rep or y==rep]
            external_degree = sum([len(edgetuples[(x,y)]) for (x,y) in selected_tuples if xor(x in orb,y in orb)])
            internal_degree = sum([len(edgetuples[(x,y)]) for (x,y) in selected_tuples if x in orb and y in orb])
            orbsortkeys[orb] = (external_degree,internal_degree,orbsize,classname,rep)
         
        # sort orbits by orbsort keys
        sorted_orbits = sorted(orbits,key = lambda x: orbsortkeys[x],reverse=True)
        return [sorted(x) for x in sorted_orbits]

    def get_merge_path(self,sorted_orbits,edgetuples):
        temp_path = [y for x in sorted_orbits for y in sorted(x)]
        mergepath = []
        orbdict = dict()
        for orb in sorted_orbits:
            for x in orb:
                orbdict[x] = orb

        while temp_path:
            mergepath.append(temp_path.pop(0))
            score = dict()
            for x in temp_path:
                adjacency_score = 0
                colocal_score = 0
                for n in mergepath:
                    adjacency_score -= len(edgetuples.get((n,x),[])) + len(edgetuples.get((x,n),[]))
                    colocal_score -= int(orbdict[x]==orbdict[n])
                score[x] = (adjacency_score,colocal_score,x)
            temp_path = sorted(temp_path,key=lambda x: score[x])
        return mergepath

    def build_merge_sequence(self,edgetuples,mergepath):

        def edgetuple_iter(new_key_dict,edgetuples):
            sorted_keys = sorted(new_key_dict.keys(),key = lambda x: (min(x),max(x)))
            for key in sorted_keys:
                edges = sorted(edgetuples[new_key_dict[key]])
                for e in edges:
                    yield key,e

        def maps_to_indices(maps,path):
                return [tuple(sorted([(path.index(x),path.index(y)) for x,y in m])) for m in maps]

        def convolve_maps(map2,map1):
            # apply map2 to map1 
                map2_dict = dict(map2)
                return tuple(sorted([ (x,map2_dict[y]) for x,y in map1 ]))

        def expand_symmetries(scaffold_symmetries,final_symmetries,path):
            ###
            # if scaffold and final symmetries identical, do nothing
            # if final symmetry is just the identity symmetry, give all symmetries
            # else
            # identify preserved symmetries (scaffold intersection final)
            # on the non-preserved symmetries,
            # # # pop each one and put on stack
            # # # rotate current one using preserved symmetries and remove from non-preserved

            if len(scaffold_symmetries) == len(final_symmetries):
                return deque()
            if len(final_symmetries)==1:
                return deque(maps_to_indices(scaffold_symmetries,path))

            stack = deque([tuple([(x,x) for x in range(0,len(path))])])
            preserved = maps_to_indices(final_symmetries,path)
            not_preserved = deque([x for x in maps_to_indices(scaffold_symmetries,path) if x not in preserved])

            while not_preserved:
                current = not_preserved.popleft()
                convolved = [convolve_maps(x,current) for x in preserved]
                for elem in [x for x in convolved if x in not_preserved]:
                    not_preserved.remove(elem)
                stack.append(current)
            return stack
                    
        def canonize_symmetries(orbits,path):
            # label nodes with path index
            # sort orbits by label
            # trim by level
            # e.g., on a 3-way symmetric graph, 
            # return {0: None, 1: (0,1), 2: (0,1,2)}

            # do shatter analysis to break within orbits
            # a tie is a variable pair on which idx1 < idx2 can be imposed
            # to shatter a group of symmetries
            # goal is to identify the minimum number of ties required to
            # shatter all symmetries
            
            symmetries = maps_to_indices(self._scaffold_symmetries,path)
            orbits_to_consider = [sorted([path.index(x) for x in orb]) for orb in orbits if len(orb) > 1]
            ties = []

            for orb in orbits_to_consider:    
                candidates = SortedSet((x,y) for sym in symmetries for (x,y) in sym if x in orb and x!=y)
                if len(symmetries)>1:
                    for tie in candidates:
                        old_length = len(symmetries)
                        symmetries = [sym for sym in symmetries if tie not in sym]
                        if len(symmetries) < old_length:
                            ties.append(tie)
            
            leveldict = dict(zip(range(0,len(path)), [None]*len(path)))
            already_checked = set()
            for i in range(len(path)):
                ties2 = [(x,y) for x,y in ties if x<=i and y<=i and (x,y) not in already_checked]
                leveldict[i] = tuple(ties2)
                already_checked.update(ties2)
            return leveldict
        
        # Assumptions: rete-node that processes an edge (class(n1),attr1,attr2,class(n2)) will store/output a token (n1,n2)
        MergeTuple = namedtuple("MergeTuple",[
            'lhs','rhs',
            'lhs_remap','rhs_remap',
            'token_length',
            'symmetry_checks'
            ])

        scaffold_symmetry_breaks = expand_symmetries(self._scaffold_symmetries,self._final_symmetries,mergepath)
        internal_symmetries = maps_to_indices(self._final_symmetries,mergepath)

        mergetuples = deque()
        symmetry_checks_dict = canonize_symmetries(self._scaffold_orbits,mergepath)
        total_edges = sum([len(x) for x in edgetuples.values()])
        if total_edges == 1:
            # case 1: pattern has only one edge
            (n1,n2),e = [x for x in edgetuples.items()][0]
            new_merge_node = MergeTuple(
                    lhs=e,
                    lhs_remap=tuple(enumerate([mergepath.index(n1),mergepath.index(n2)])),
                    rhs=None,
                    rhs_remap=None,
                    token_length=2,
                    symmetry_checks = symmetry_checks_dict[1],
                )
            mergetuples.append(new_merge_node)
            return mergetuples, scaffold_symmetry_breaks, internal_symmetries
        
        # case 2: pattern has multiple edges
        # first change varpairs to indices
        new_key_dict = {(mergepath.index(x),mergepath.index(y)):(x,y) for (x,y) in edgetuples.keys()}
        edgelist = edgetuple_iter(new_key_dict,edgetuples)
        rhs,rhs_remap,symchecks = None, None, None
        for i,(key,e) in enumerate(edgelist):
            if i==0:
                # seed LHS
                lhs = e
                lhs_remap = tuple(enumerate(key))
                current_path = set(key)
                current_length = 2
                continue
            # current RHS
            rhs = e
            rhs_remap = tuple(enumerate(key))
            current_path.update(key)
            current_length = len(current_path)
            new_merge_node = MergeTuple(
                    lhs=lhs,
                    lhs_remap=lhs_remap,
                    rhs=rhs,
                    rhs_remap=rhs_remap,
                    token_length = current_length,
                    symmetry_checks = symmetry_checks_dict[current_length-1],
                )
            mergetuples.append(new_merge_node)

            # now recompute lhs
            lhs = new_merge_node
            lhs_remap = tuple(enumerate(range(0,current_length)))
            
        return mergetuples,scaffold_symmetry_breaks, internal_symmetries

    def get_attrtuples(self):
        attrtuples = dict()
        attrtuple_set = set()
        AttrTuple = namedtuple("AttrTuple",['cls','attr'])
        if self._deps is not None:
            simple_attribute_calls = set.union(*[dep['attributes'] for dep in self._deps]) 
            dynamic_attribute_calls = set()
            varmethods_to_check = set.union(*[dep['varmethods'] for dep in self._deps])
            for var,varmethod,kws in varmethods_to_check:
                arguments = self[var].get_dynamic_methods()[varmethod]._args
                attrs = self[var].get_literal_attrs()
                attrdeps = [x for x in arguments if x in attrs]
                for x in attrdeps:
                    dynamic_attribute_calls.add( (var,x,))
            
            attrtuples = dict()
            for var,attr in (simple_attribute_calls|dynamic_attribute_calls):
                _cls =self[var].__class__
                if var not in attrtuples:
                    attrtuples[var] = deque()
                a = AttrTuple(cls=_cls,attr=attr)
                attrtuples[var].append(a)
                attrtuple_set.add(a)

            for var in attrtuples:
                attrtuples[var] = tuple(sorted(attrtuples[var]))
        return attrtuples,attrtuple_set

    def get_computed_variables(self):
        variables = []
        for dep in self._deps:
            for item in dep['assignments']:
                variables.append(item)
        return variables

    def build_rete_subset(self):
        # classtuples {node.id: (class,class,class,Entity)}
        # edgetuples {(node1.id,node2.id): [(class1,attr1,attr2,class2),...]}, where attr1 < attr2
        # mergetuples [ MergeTuple(lhs=merge/edge tuple,rhs=...,
        #                          lhs_remap=[(path.index,lhs_nodes.index),rhs_remap=...],
        #                          token_length=n,prune_symmetries=[...]) ]
        # attrtuples { node.id: (class,var) }
        #classtuples, classtuple_set = self.get_classtuple_paths()
        edgetuples, edgetuple_set = self.get_edgetuples()
        sorted_orbits = self.sort_orbits(edgetuples)
        mergepath = self.get_merge_path(sorted_orbits,edgetuples)
        if len(self.variable_names)==1:
            ClassTuple = namedtuple("ClassTuple",["cls"])
            c = ClassTuple(cls=self[self.variable_names[0]])
            mergetuples = deque([c])
            scaffold_symmetry_breaks = ()
            internal_symmetries = ((0,0),)
        else:
            mergetuples,scaffold_symmetry_breaks, internal_symmetries = self.build_merge_sequence(edgetuples,mergepath)
        
        def maps_to_indices(maps,path):
            return [tuple(sorted([(path.index(x),path.index(y)) for x,y in m])) for m in maps]
        
        attrtuples, attrtuple_set = self.get_attrtuples()

        # building internal dependency graph for pattern
        attr_dependency_table = defaultdict(list)
        for var,attrs in attrtuples.items():
            for attrtuple in attrs:
                bisect.insort(attr_dependency_table[attrtuple],mergepath.index(var))

        for attrtuple in attr_dependency_table.keys():
            attr_dependency_table[attrtuple] = tuple(attr_dependency_table[attrtuple])
        attr_relations = [tuple(x) for x in attr_dependency_table.items()]

        # now build final patterntuple
        # name - pattern name
        # scaffold - mergetuple
        # attrs dict {attrtuple: (indices to check)}
        
        # if number of nodes==1
        # scaffold = MergeTuple(ClassTuple) node
        # if number of edges==1
        # scaffold = MergeTuple(EdgeTuple) node 
        # if number of edges > 1
        # scaffold = MergeTuple node w/ symmetry_checks

        computed_vars = self.get_computed_variables()

        
        PatternTuple = namedtuple('PatternTuple',[
            'scaffold','scaffold_symmetry_breaks', 'internal_symmetries',
            'attrs',
            ])

        new_pat = PatternTuple(
            scaffold = mergetuples[-1],
            scaffold_symmetry_breaks = tuple(scaffold_symmetry_breaks),
            internal_symmetries = tuple(internal_symmetries),
            attrs = tuple(attr_relations),
            )

        # Pattern relations cannot be specified here.
        # They have to be analyzed globally
        return {'name':self.id, 
        'edges':edgetuple_set, 
        'attrs':attrtuple_set, 
        'merges':mergetuples, 
        'pattern_tuple': new_pat,
        'pattern':self,
        'node_variables': tuple(mergepath),
        'computed_variables': tuple(computed_vars)
        }
        


def main():
    pass


if __name__ == '__main__':
    main()
