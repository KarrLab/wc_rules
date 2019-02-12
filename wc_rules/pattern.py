from .indexer import DictLike
from .utils import generate_id,ValidateError
from .expr_parse import parse_expression
from .expr2 import parser, Serializer, prune_tree, simplify_tree, BuiltinHook, PatternHook, get_dependencies
from operator import lt,le,eq,ne,ge,gt
import random
import pprint
from collections import deque,defaultdict
from . import graph_utils as gr

class Pattern(DictLike):
    def __init__(self,idx,nodelist=None,recurse=True):
        super().__init__()
        self.id = idx
        self._constraints = ''
        self._finalize = False
        self._tree = None
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

    def validate_dependencies(self):
        deps = get_dependencies(self._tree)

        final_deps = defaultdict(set)
        final_deps['variables'] = set([x.id for x in self])

        constants = BuiltinHook.allowed_constants
        builtins = BuiltinHook.allowed_functions

        for dep in deps:
            print(dep)
            # check variables
            for var in sorted(dep['variables']):
                if var not in final_deps['variables'] | final_deps['assignments'] | constants:
                    raise ValidateError('Variable ' + var + ' not found in pattern ' + self.id)
            for var,attr in sorted(dep['attributes']):
                if var in final_deps['variables']:
                    if attr not in self[var].get_literal_attributes():
                        raise ValidateError('Attribute ' + attr + ' not found in variable ' + var)
            for var, fname, kws in sorted(dep['varmethods']):
                if var in final_deps['variables']:
                    fns_dict = self[var].get_dynamic_methods()
                    if fname not in fns_dict:
                        raise ValidateError('Method ' + fname + ' not found in variable ' + var)
                    fn = fns_dict[fname]
                    if kws is not None:
                        for kw in kws:
                            if kw not in fn._vars:
                                raise ValidateError('Keyword ' + kw + ' not found in method ' + var + '.' + fname)
            for var in dep['assignments']:
                final_deps['assignments'].add(var)
            for fn in dep['builtins']:
                if fn not in builtins:
                    raise ValidateError('Builtin function ' + fn + ' not found')
                            

        return final_deps

    def validate_pattern_connectivity(self):
        # ensure there are no neighbour nodes not in pattern
        examined = set()
        
        start_node = self[min(self._dict.keys())]
        stack = deque([start_node])        
        while len(stack)>0:
            current_node = stack.popleft()
            assert current_node in self
            neighbours = set(current_node.listget_all_related()) - examined
            examined.add(current_node)
            stack.extendleft(list(neighbours))

        # ensure pattern is fully connected
        assert sorted([x.id for x in examined])==sorted(self.keys())
        return self

    def parse_constraints(self):
        tree = parser.parse(self._constraints)
        tree = prune_tree(tree)
        modified = True
        # simplify constraints as much as possible
        while modified:
            tree,modified = simplify_tree(tree)
        return tree

    def finalize(self): 
        
        self.validate_pattern_connectivity()
        self._tree = self.parse_constraints()

        # get reference & defined dependencies
        compiled_deps = self.validate_dependencies()
        
        # here we build a networkx graph to evaluate symmetry
        g,helper = gr.build_simple_graph(self)

        # use get dependencies to attach nodes referring to attributes & functions



        #print(tree.pretty())
        #print(tree)
        #evaluators = Serializer(h=BuiltinHook(),p=PatternHook()).transform(tree)
        #print(evaluators)
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
