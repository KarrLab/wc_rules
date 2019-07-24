from lark import Lark, tree, Transformer,Visitor, v_args, Tree,Token
from collections import defaultdict,namedtuple
import builtins,math
from attrdict import AttrDict
from pprint import pformat, pprint
from functools import partial
from .utils import ValidateError
import networkx

# DO NOT USE CAPS
grammar = """
%import common.CNAME
%import common.WS_INLINE
%import common.NUMBER
%ignore WS_INLINE
%import common.ESCAPED_STRING
%import common.NEWLINE

COMMENT: /#.*/
%ignore COMMENT
%ignore NEWLINE

    ?literal.1: NUMBER -> number | "True"-> true | "False" -> false | ESCAPED_STRING -> string
    ?atom: literal | function_call | "(" expression ")" 

    function_name: CNAME
    variable: CNAME
    attribute: CNAME

    arg: expression
    kw: CNAME
    kwarg: kw "=" arg
    args: arg ("," arg )*
    kwargs: kwarg ("," kwarg)*
    
    function_call: variable "." function_name "(" [kwargs] ")"
        | function_name "(" [args] ")"
        | function_name "(" match_expression ")"
        | variable "." attribute 
        | variable
        
    ?sum: term (add_op term)*
    ?term: factor (mul_op factor)* 
    ?factor: factor_op factor | atom

    ?factor_op: "+" -> noflip | "-" -> flipsign
    ?add_op: "+" -> add | "-" -> subtract
    ?mul_op: "*" -> multiply | "/" -> divide    

    ?expression: sum

    boolean_expression: expression bool_op expression
    
    ?bool_op: ">=" -> geq | "<=" -> leq | ">" -> ge | "<" -> le | "==" -> eq | "!=" -> ne
    
    pattern: CNAME
    pattern_variable:CNAME
    varpair: pattern_variable ":" variable
    varpairs: varpair ("," varpair)*
    match_expression: "{" varpairs "}" "in" pattern

    assignment: declared_variable "=" (expression|boolean_expression)
    declared_variable: CNAME

    expressions: (assignment|boolean_expression) (NEWLINE (assignment|boolean_expression))* 
    ?start: [NEWLINE] expressions [NEWLINE]
"""

parser = Lark(grammar, start='start')

def node_to_str(node):
    return node.children[0].__str__()

def prune_tree(tree):
    # remove newline tokens
    nodes = list(filter(lambda x:x.__class__.__name__=='Token',tree.children))
    for node in list(nodes):
        tree.children.remove(node)
    return tree

def simplify_tree(tree): 
    # here, we reshape and simplify the tree
    modified = False
    
    # find parent->factor->noflip,item
    # replace with parent->item
    # e.g., +x to x
    nodes = find_parents_of(tree,'factor')
    for node in nodes:
        # get their factor children that have noflip children
        factors = [x for x in node.children 
            if getattr(x,'data','')=='factor'
            and x.children[0].data=='noflip'
            ]
        modified = modified or len(factors)>0
        for factor in factors:
            ind = node.children.index(factor)
            node.children[ind] = factor.children[1]

    # find parent->factor1->flipsign,factor2->flipsign,item
    # replace with parent->item
    # e.g., --x to x
    nodes = find_parents_of(tree,'factor')
    ignored = []
    for node in nodes:
        if node in ignored:
            continue
        factors = [x for x in node.children 
            if getattr(x,'data','')=='factor'
            and x.children[0].data=='flipsign'
            and x.children[1].data=='factor'
            and x.children[1].children[0].data =='flipsign'
            ]
        modified = modified or len(factors)>0
        for factor in factors:
            ignored.append(factor.children[1])
            ind = node.children.index(factor)
            node.children[ind] = factor.children[1].children[1]

    # insert 'multiply' as first item in all data=='term'
    nodes = list(tree.find_data('term'))
    for node in nodes:
        if getattr(node.children[0],'data','') not in ['multiply','divide']:
            node.children.insert(0,Tree(data='multiply',children=[]))

    # identify parent -> multiply, term -> items 
    # replace with parent -> items
    # identify parent -> divide,term -> items
    # replace with parent -> flipped(items)
    collapsible = False
    for node in nodes:
        for i in range(len(node.children)-1):
            if getattr(node.children[i],'data','')=='multiply' and getattr(node.children[i+1],'data','')=='term':
                collapsible = True
                insert_this = node.children[i+1].children
            if getattr(node.children[i],'data','')=='divide' and getattr(node.children[i+1],'data','')=='term':
                collapsible = True
                insert_this = []
                for term in node.children[i+1].children:
                    if getattr(term,'data','')=='multiply':
                        insert_this.append(Tree(data='divide',children=[]))
                    elif getattr(term,'data','')=='divide':
                        insert_this.append(Tree(data='multiply',children=[]))
                    else:
                        insert_this.append(term)
            if collapsible:
                del node.children[i:i+2]
                node.children[i:i] = insert_this
                break
        if collapsible:
            break
    modified = modified or collapsible

    #first insert 'add' as first token of sums
    nodes = list(tree.find_data('sum'))
    for node in nodes:
        if getattr(node.children[0],'data','') not in ['add','subtract']:
            node.children.insert(0,Tree(data='add',children=[]))
    # find sum -> add, sum -> items
    # replace with sum -> items
    # e.g., x + (y+z) to x + y + z
    # find sum -> subtract, sum -> items
    # replace with sum -> flipped(items)
    # e.g., x - (y+z) to x - y - z
    collapsible = False
    for node in nodes:
        for i in range(len(node.children)-1):
            if getattr(node.children[i],'data','')=='add' and getattr(node.children[i+1],'data','')=='sum':
                collapsible = True
                insert_this = node.children[i+1].children
            if getattr(node.children[i],'data','')=='subtract' and getattr(node.children[i+1],'data','')=='sum':
                collapsible = True
                insert_this = []
                for term in node.children[i+1].children:
                    if getattr(term,'data','')=='add':
                        insert_this.append(Tree(data='subtract',children=[]))
                    elif getattr(term,'data','')=='subtract':
                        insert_this.append(Tree(data='add',children=[]))
                    else:
                        insert_this.append(term)
            if collapsible:
                del node.children[i:i+2]
                node.children[i:i] = insert_this
                break
        if collapsible:
            break
    modified = modified or collapsible

    # find sum -> subtract,factor->flipsign,item
    # replace with sum -> add, item
    # e.g., x - (-y) + z to x + y + z
    nodes = list(tree.find_data('sum'))
    for node in nodes:
        subtract_index = [
        i for i,x in enumerate(node.children)
            if getattr(x,'data','')=='subtract'
            and getattr(node.children[i+1],'data','')=='factor'
            and getattr(node.children[i+1].children[0],'data','')=='flipsign'
            ]

        modified = modified or len(subtract_index)>0
        for i in subtract_index:
            item = node.children[i+1].children[1]
            node.children[i] = Tree(data='add',children=[])
            node.children[i+1] = item

    return (tree,modified)

def find_parents_of(tree,data):
    f = lambda t: any([getattr(x,'data','')==data for x in t.children])
    return tree.find_pred(f)    

def detect_edge(tree,data1,data2):
    # returns tuplist of [(node,nodelist), (node,nodelist)]
    # where nodelist is a sublist of node.children
    nodes = tree.find_data(data1)
    tuplist = []
    for node in nodes:
        nodelist = list(node.find_data(data2))
        if len(nodelist) > 0:
            tuplist.append( (node,nodelist) )
    return tuplist


def get_dependencies(tree):
    deplist = []
    for expr in tree.children:
        deps = defaultdict(set)
        # first get all function call nodes
        if expr.data=='assignment':
            var = node_to_str(expr.children[0])
            deps['assignments'].add(var)
        funcnodes = expr.find_pred(lambda x: x.data=='function_call')
        for node in funcnodes:
            ch = node.children
            function_call_type = tuple([x.data for x in ch])
            
            if function_call_type == ('variable',):
                var = node_to_str(ch[0])
                deps['variables'].add(var)
            elif function_call_type == ('variable','attribute'):
                var,attr = [node_to_str(x) for x in ch]
                deps['variables'].add(var)
                deps['attributes'].add( (var,attr) )
            elif function_call_type == ('variable','function_name'):
                var,func = [node_to_str(x) for x in ch]
                deps['variables'].add(var)
                deps['varmethods'].add( (var,func,None) )
            elif function_call_type == ('variable','function_name','kwargs'):
                var,func,_ = [node_to_str(x) for x in ch]
                kwargs = ch[2].children
                kws = tuple(sorted([node_to_str(x.children[0]) for x in kwargs]))
                deps['variables'].add(var)
                deps['varmethods'].add( (var,func,kws) )
            elif function_call_type  in [('function_name','args'),('function_name',)]:
                function_name = node_to_str(ch[0])
                deps['builtins'].add(function_name)
            elif function_call_type == ('function_name','match_expression'):
                function_name = node_to_str(ch[0])
                node = ch[1]
                pattern = node_to_str(node.children[1])
                deps['matchfuncs'].add(function_name)
                deps['patterns'].add(pattern)
                
                varpairs = node.children[0].children
                vpairs = []
                for varpair in varpairs:
                    pvar = node_to_str(varpair.children[0])
                    lvar = node_to_str(varpair.children[1])
                    vpairs.append(tuple([pvar,lvar]))
                deps['patternvarpairs'].add( tuple([pattern,tuple(vpairs)]))
            
        deplist.append(deps)
    return deplist


ExprGraphNode = namedtuple('ExprGN',['category','name','matching'])

class NodeCounter(object):
    def __init__(self):
        self.n = -1

    def gen_new_node(self):
        self.n += 1
        return NodeRef(self.n)


class NodeRef(object):
    def __init__(self,v):
        self._v = v

    def increment(self):
        self._v += 1

    def __hash__(self): return hash(self._v)

    def __eq__(self,other):
        return self._v == other._v

    def __repr__(self):
        return 'NodeRef('+str(self._v)+')'
    pass

def add_new_node(graph,counter,category,name,matching=''):
    data = ExprGraphNode(category = category,name = name,matching=matching)
    # category is used sort nodes
    # name is used to identify individual nodes on the graph
    # category + matching is used to match nodes.
    new_id = counter.gen_new_node()
    graph.add_node(new_id,data=data)
    return (graph,counter,new_id)


def build_simple_graph(dictlike):
    
    G = networkx.DiGraph()
    #print(G.edges(data=True))
    counter = NodeCounter()
    node_dict = defaultdict(dict)
        
    # add variables
    for node in dictlike:
        G,counter,new_id = add_new_node(G,counter,'variable',node.id,node.__class__.__name__)
        node_dict['variables'][node.id] = new_id
    
    # add edges
    visited = set()
    for node in dictlike:
        if node not in visited:
            attrs = node.get_nonempty_related_attributes()
            for attr in attrs:
                related_attr = node.get_related_name(attr)
                for node2 in node.listget(attr):        
                    if node2 not in visited:
                        id1 = node_dict['variables'][node.id]
                        id2 = node_dict['variables'][node2.id]
                        if id2 not in G.neighbors(id1):
                            G.add_edge(id1,id2,label=set())
                            G.add_edge(id2,id1,label=set())
                        G[id1][id2]['label'].add((attr,related_attr,))
                        G[id2][id1]['label'].add((related_attr,attr,))
                        #if attr <= related_attr:
                        #    G.add_edge(id1,id2,label=(attr,related_attr))
                        #if attr >= related_attr:
                        #    G.add_edge(id2,id1,label=(related_attr,attr))
                        #print(G.edges(data=True))
                    # note the edge gets added twice if attr==related_attr
                    # this is okay!
            

    return G,node_dict,counter

def build_graph_for_symmetry_analysis(G,node_dict,counter,deps,tree):
    if deps is None:
        return (G,node_dict)
    for dep in deps:
        # add assigned variables
        for var in dep['assignments']:
            G,counter,new_id = add_new_node(G,counter,'variable',var)
            node_dict['variables'][var] = new_id

        # add attributes
        for var,attr in dep['attributes']:
            if tuple([var,attr]) not in node_dict['attributes']:
                G,counter,new_id = add_new_node(G,counter,'attribute',attr,attr)
                var_id = node_dict['variables'][var]
                G.add_edge(var_id,new_id,label='')
                node_dict['attributes'][tuple([var,attr])] = new_id

        # add varmethods
        for var,fname,kws in dep['varmethods']:
            if tuple([var,fname]) not in node_dict['functions']:
                G,counter,new_id = add_new_node(G,counter,'function',fname,fname)
                var_id = node_dict['variables'][var]
                G.add_edge(var_id,new_id,label='')
                node_dict['functions'][tuple([var,fname])] = new_id

        for fname in dep['builtins']:
            if fname not in node_dict['functions']:
                G,counter,new_id = add_new_node(G,counter,'function',fname,fname)
                node_dict['functions'][fname] = new_id
        
        for fname in dep['matchfuncs']:
            if fname not in node_dict['functions']:
                G,counter,new_id = add_new_node(G,counter,'function',fname,fname)
                node_dict['functions'][fname] = new_id

        for pat in dep['patterns']:
            if pat not in node_dict['patterns']:
                G,counter,new_id = add_new_node(G,counter,'pattern',pat,pat)
                node_dict['patterns'][pat] = new_id

    graphbuilder = GraphBuilder(G,node_dict,counter)
    G,node_dict = graphbuilder.transform(tree)
    return (G,node_dict)

class GraphBuilder(Transformer):

    def __init__(self,graph,node_dict,counter):
        self.graph = graph
        self.node_dict = node_dict
        self.counter = counter

    def check_node_exists(self,category,val):
        return val in self.node_dict[category]

    def add_new_node(self,category,name=None,matching=''):
        new_id = self.counter.gen_new_node()
        if name is None:
            name = category + '_'+ str(new_id._v)
        data = ExprGraphNode(category = category,name = name,matching=matching)
        self.graph.add_node(new_id,data=data)
        self.node_dict[category][name] = new_id
        return new_id

    def add_to_category(category,name_is_matching=False):
        def inner(slf,args):
            val = args[0].__str__()
            matching = ''
            if name_is_matching:
                matching = val
            if slf.check_node_exists(category,val):
                return slf.node_dict[category][val]
            new_id = slf.add_new_node(category,val,matching)
            return new_id
        return inner

    def add_op(opcateg,op):
        return lambda x,y: x.add_new_node(opcateg,matching=op)

    def n2s(self,arg): return arg[0].__str__()
    def pass_on(self,arg): return arg[0]
    
    number = add_to_category('literals',name_is_matching=True)
    string = add_to_category('literals',name_is_matching=True)
    variable = add_to_category('variables',name_is_matching=False)
    pattern = add_to_category('patterns',name_is_matching=True)
    function_name = n2s
    attribute = n2s
    kw = n2s
    kwarg = tuple
    kwargs = list
    arg = pass_on
    pattern_variable = n2s
    varpair = tuple
    varpairs = list
    expression = pass_on
    declared_variable = variable

    def args(self,args):
        return [(i,a) for i,a in enumerate(args)]

    eq = add_op('compare_op','eq')
    ne = add_op('compare_op','ne')
    le = add_op('compare_op','le')
    ge = add_op('compare_op','ge')
    leq = add_op('compare_op','leq')
    geq = add_op('compare_op','geq')
   

    def true(self,args):
        new_id = self.add_new_node('literals','True','True')
        return new_id

    def false(self,args):
        new_id = self.add_new_node('literals','False','False')
        return new_id

    def function_call(self,args):
        # function_call: variable "." function_name "(" [kwargs] ")"
        #  | function_name "(" [args] ")"
        #  | function_name "(" match_expression ")"
        #  | variable "." attribute 
        #  | variable

        # what is the first arg? if it is a noderef it is a variable
        nodes_to_return = []
        if isinstance(args[0],NodeRef):
            # its a variable
            var = self.graph.nodes[args[0]]['data'].name
            if len(args) == 1:
                # function_call := variable
                nodes_to_return.append(args[0])
            elif (var,args[1]) in self.node_dict['attributes']:
                # function_call := variable "." attribute
                nodes_to_return.append(self.node_dict['attributes'][(var,args[1])])
            elif (var,args[1]) in self.node_dict['functions']:
                # function_call := variable "." function_name [kwargs]
                nodes_to_return.append(self.node_dict['functions'][(var,args[1])])
                if len(args)>2:
                    # kwargs exists
                    new_kwargs_node = self.add_new_node('kwargs')
                    nodes_to_return.append(new_kwargs_node)
                    kwargs = args[2]
                    for kw,ref in kwargs:
                        self.graph.add_edge(ref,new_kwargs_node,label=kw)
            else:
                raise ValidateError('Function call could not be found.')
        elif isinstance(args[0],str):
            # # function_call := function_name [args/match_expression]
            fname = args[0]
            node_ref = self.node_dict['functions'][fname]
            nodes_to_return.append(node_ref)
            if len(args) > 1:
                # does it have args/matchexpression
                new_args_node = self.add_new_node('args')
                for i,n in args[1]:
                    self.graph.add_edge(n,new_args_node,label=str(i))
                nodes_to_return.append(new_args_node)
        else:
            raise ValidateError('Function call could not be found.')

        if len(nodes_to_return) == 1:
            return nodes_to_return[0]
        
        new_funccall_node = self.add_new_node('function_call')
        for node in nodes_to_return:
            self.graph.add_edge(node,new_funccall_node,label='')    
        return new_funccall_node

    def match_expression(self,args):
        varpairs = args[0]
        pattern = args[1]

        new_varpairs_node = self.add_new_node('varpairs')
        for pvar,var in varpairs:
            self.graph.add_edge(var,new_varpairs_node,label=pvar)
        new_matchexpr_node = self.add_new_node('match_expression')
        
        self.graph.add_edge(new_varpairs_node,new_matchexpr_node,label='')
        self.graph.add_edge(pattern,new_matchexpr_node,label='')

        return [(0,new_matchexpr_node)]

    
    cmp_ops = ['eq','ne','ge','le','geq','leq']
    lhs_label_dict = dict(zip(cmp_ops,['']*2 + ['lhs']*4))
    rhs_label_dict = dict(zip(cmp_ops,['']*2 + ['rhs']*4))
        
    def boolean_expression(self,args):

        if len(args)==1:
            lhs = args[0]
            op = self.eq([])
            rhs = self.true([])

        else:
            lhs = args[0]
            op = args[1]
            rhs = args[2]

        oplabel = self.graph.nodes[op]['data'].matching
        lhs_label = self.lhs_label_dict[oplabel]
        rhs_label = self.rhs_label_dict[oplabel]
        
        self.graph.add_edge(lhs,op,label=lhs_label)
        self.graph.add_edge(rhs,op,label=rhs_label)
        
        return op

    # ?sum: term (add_op term)*
    # ?term: factor (mul_op factor)* 
    # ?factor: factor_op factor | atom

    # ?factor_op: "+" -> noflip | "-" -> flipsign
    # ?add_op: "+" -> add | "-" -> subtract
    #?mul_op: "*" -> multiply | "/" -> divide

    def factor(self,args):
        # assuming it has been simplified
        if len(args)==2:
            new_flip_node = self.add_new_node('flipsign')
            self.graph.add_edge(args[1],new_flip_node,label='')
            return new_flip_node
        return args[0]

    def constant(s): return lambda x,y: s
    add = constant('add')
    subtract = constant('subtract')
    multiply = constant('multiply')
    divide = constant('divide')

    def term(self,args):
        chunks = [args[i:i + 2] for i in range(0, len(args), 2)]
        if len(chunks)==1 and chunks[0][0]=='multiply':
            return chunks[0][1]
        new_term_node = self.add_new_node('term')
        for op,ref in chunks:
            self.graph.add_edge(ref,new_term_node,label=op)
        return new_term_node
        
    def sum(self,args):
        chunks = [args[i:i + 2] for i in range(0, len(args), 2)]
        if len(chunks)==1 and chunks[0][0]=='add':
            return chunks[0][1]
        new_sum_node = self.add_new_node('sum')
        for op,ref in chunks:
            self.graph.add_edge(ref,new_sum_node,label=op)
        return new_sum_node
        
    def assignment(self,args):
        declared_var = args[0]
        expr = args[1]
        self.graph.add_edge(expr,declared_var,label='assignment')
        return declared_var

    def expressions(self,args):
        return (self.graph,self.node_dict)

class BuiltinHook(object):
    # this class holds the builtin functions accessible to expressions constraining patterns

    allowed_functions =  set([
    'abs', 'ceil', 'factorial', 'floor', 'exp', 'expm1', 'log', 'log1p', 'log2', 'log10',
    'pow', 'sqrt', 'acos', 'asin', 'atan', 'atan2', 'cos', 'hypot', 'sin', 'tan', 'degrees', 'radians', 
    'max', 'min', 'sum', 'any', 'all', 'inv',
    ])

    allowed_constants = set([
    'pi','tau','avo',
    ])

    abs = math.fabs
    ceil = math.ceil
    factorial = math.factorial
    floor = math.floor
    exp = math.exp
    expm1 = math.expm1
    log = math.log
    log1p = math.log1p
    log2 = math.log2
    log10 = math.log10
    pow = math.pow
    sqrt = math.sqrt
    acos = math.acos
    asin = math.asin
    atan = math.atan
    atan2 = math.atan2
    cos = math.cos
    hypot = math.hypot
    sin = math.sin
    tan = math.tan
    pi = math.pi
    tau = math.tau
    avo = 6.02214076e23 
    degrees = math.degrees
    radians = math.radians

    max = builtins.max
    min = builtins.min

    @staticmethod
    def sum(*args): return math.fsum(args)
    @staticmethod
    def any(*args): return builtins.any(args)
    @staticmethod
    def all(*args): return builtins.all(args)
    @staticmethod
    def inv(arg): return not arg

class PatternHook(object):
    # this class handles match expressions and match counts

    allowed_methods = ['count','exists','expand','nexists']
    
    def count(pattern=None,varpairs=None):
        # this method should access the filter method on ReteNet pattern nodes
        assert pattern is not None and varpairs is not None
        return 10

    def exists(pattern=None,varpairs=None):
        assert pattern is not None and varpairs is not None
        return True


class MatchLocal(AttrDict):
    # dict holding match variables and additional declared variables
    def __init__(self,match={}):
        super().__init__(match)

    def __getattr__(self,key):
        if key in self:
            return self[key]
        return None



class Serializer(Transformer):
    # m for match, h for expressionhook, p for patternhook

    # strategy: wrap all function calls into a 'x.do(match=m,params=dict)' method
    
    allowed_functions = ['count','exists','nexists']
    '''
    def __init__(self,h,p):
        self.expression_hook = h
        self.pattern_hook = p
    '''
    
    def join_strings(self,args): return " ".join(args)
    def constant(s): return lambda x,y: s
    def n2s(self,arg): return arg[0].__str__()

    
    def expressions(self,args):
        return [x for x in args if x.__class__.__name__ != 'Token']
    
    def varpair(self,args):
        patternvar = self.n2s(args[0].children)
        var = self.n2s(args[1].children)
        return patternvar+":"+var

    def varpairs(self,args):
        return "{" + ",".join(args) + "}"

    def match_expression(self,args):
        varpairs = args[0]
        pattern = args[1]
        s1,s2 = ['varpairs',"=",varpairs],['pattern',"=",pattern]
        return [",".join([" ".join(x) for x in [s1,s2]])]

    def function_call(self,args):
        names = []
        arglist = []
        is_a_function = False
        if args[0].data == 'variable':
            s = self.n2s(args[0].children)
            if s in ['pi','avo','tau']:
                assert len(args)==1
                names.extend(['h',s])
            else:
                names.extend(['m',s])
                if len(args) > 1:
                    if args[1].data == 'attribute':
                        names.append(self.n2s(args[1].children))
                    elif args[1].data == 'function_name':
                        is_a_function = True
                        names.append(self.n2s(args[1].children))
                        if len(args)>2:
                            arglist = args[2]
        elif args[0].data == 'function_name':
            is_a_function = True
            s = self.n2s(args[0].children)
            if s in ['count','exists','nexists']:
                names.append('p')
            names.append(s)
            if len(args) > 1:
                arglist = args[1]
        if not is_a_function:
            return ".".join(names)
        return ".".join(names) + "(" + ",".join(arglist) + ")"


    geq = constant('>=')
    leq = constant('<=')
    ge = constant('>')
    le = constant('<')
    eq = constant('==')
    ne = constant('!=')
    true = constant('True')
    false = constant('False')
    number = n2s
    string = n2s
    kw = n2s
    arg = join_strings   
    args = list
    kwarg = lambda self,args: "=".join(args)
    kwargs = list
    pattern = n2s
    
    boolean_expression = list
    
space_join = lambda x: " ".join(x)
comma_join = lambda x: ",".join(x)
simple_join = lambda x: "".join(x)
enclose = lambda x: "(" + x + ")"
enclose_sq = lambda x: "[" + x + "]"
enclose_quote = lambda x: "'" + x + "'"
symbol_join = lambda x,y: "".join([" ",y," "]).join(x)
has_keys = lambda d,x: all([y in d for y in x])
not_has_keys = lambda d,x: not any([y in d for y in x])
tuplize = lambda x: "(" + ",".join(x) + "," + ")"


class Serializer2(Transformer):

    # naming conventions for lambda parameters
    # x: hook for rete node (x.do() is the default function called. also match related fns x.exist(), etc
    # h: hook for builtins (h.xxx() for any xxx in builtinhook class)
    # m: hook for current match being evaluated.

    def join_strings(self,args): return " ".join(args)
    def constant(s): return lambda x,y: s
    def n2s(self,arg): return arg[0].__str__()

    def category_pair(cat):
        return lambda x,y: (cat,enclose_quote(y[0].__str__()))

    #literals and operators, convert to strings
    number = string = n2s    
    geq = constant(">=")
    leq = constant("<=")
    ge = constant(">")
    le = constant("<")
    eq = constant("==")
    ne = constant("ne")
    true = constant("True")
    false = constant("False")
    flipsign = subtract = constant("-")
    add = constant("+")
    multiply = constant("*")
    divide = constant("/")

    
    # things that are converted to category pairs, e.g., ('variable','x1')
    #function_name = variable =  attribute = kw = pattern = pattern_variable = declared_variable = CNAME
    function_name = category_pair('function_name')
    variable = category_pair('variable')
    attribute = category_pair('attribute')
    #kw = category_pair('kw')
    pattern = category_pair('pattern')
    pattern_variable=category_pair('pattern_variable')
    declared_variable = category_pair('declared_variable')

    # things that compile
    arg = lambda x,y:y[0].__str__()
    kw = lambda x,y:enclose_quote(y[0].__str__())
    kwarg = tuple
    varpair = lambda x,y: tuplize([y[0][1],y[1][1]])
    
    def args(self,args):
        return ('args',args)

    def kwargs(self,args):
        return ('kwargs',tuplize([tuplize(arg) for arg in args]))

    def varpairs(self,args):
        return ('varpairs',tuplize(args))

        
    def xdo(self,args):
        return simple_join(['x.do',enclose(comma_join([space_join([x,"=",y]) for x,y in args + [('match','m')] ]))])
    
    def match_expression(self,args):
        # match_expression is always an arg to some other function
        return ('args',[self.xdo(args)])
    
    def function_call(self,args):
        params = dict(args)
        if has_keys(params,['function_name']) and not_has_keys(params,['variable']):
            # is a builtin or a 
            # strip enclosing quotes
            name = params['function_name'].strip("'")
            prefix = 'h.'
            str_args = comma_join(params.get('args',[]))
            if name in ['exists','nexists','count']:
                # compile first get the function that gets the match object
                prefix = 'x.'
            return simple_join([prefix,name,enclose(str_args)])
        # all others get processed as x.do() functions
        return self.xdo(args)

    ### mathematical and logical joining, always get strings to join
    sum = lambda x,y: space_join(y[1:])
    term = lambda x,y: simple_join(y[1:])
    factor = lambda x,y: enclose(space_join(y))
    boolean_expression = lambda x,y: space_join(y)

    def assignment(self,args):
        return (args[0][1].strip("'"),args[1])

    def expressions(self,args):
        # output, each expression has the form
        # ('boolean', lambda), where evaluating the lambda gives True/False
        # ('assignment',varname,lambda) where evaluating lambda gives value to be attached to varname
        final_expressions = []
        prefix = 'lambda x,h,m: '
        for arg in args:
            if isinstance(arg,str):
                final_expressions.append(('boolean',prefix + arg))
            else:
                final_expressions.append(('assignment',arg[0],prefix + arg[1]))
        return final_expressions



