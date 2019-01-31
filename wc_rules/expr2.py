from lark import Lark, tree, Transformer,Visitor, v_args, Tree,Token
from collections import defaultdict
import builtins,math
from attrdict import AttrDict
from pprint import pformat, pprint
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

    arg: expression|boolean_expression
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
        | expression
    
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
                deps['varfunctions'].add( (var,func,None) )
            elif function_call_type == ('variable','function_name','kwargs'):
                var,func,_ = [node_to_str(x) for x in ch]
                kwargs = ch[2].children
                kws = tuple(sorted([node_to_str(x.children[0]) for x in kwargs]))
                deps['variables'].add(var)
                deps['varfunctions'].add( (var,func,kws) )
            elif function_call_type  in [('function_name','args'),('function_name',)]:
                function_name = node_to_str(ch[0])
                deps['builtins'].add(function_name)
        matchnodes = expr.find_pred(lambda x: x.data == 'match_expression')
        for node in matchnodes:
            pattern = node_to_str(node.children[1])
            deps['patterns'].add(pattern)
            varpairs = node.children[0].children
            pvars = []
            for varpair in varpairs:
                pvars.append(node_to_str(varpair.children[0]))
            deps['patternvars'].add( tuple([pattern,tuple(pvars)]))
        deplist.append(deps)
    return deplist

class BuiltinHook(object):
    # this class holds the builtin functions accessible to expressions constraining patterns

    allowed_functions =  [
    'abs', 'ceil', 'factorial', 'floor', 'exp', 'expm1', 'log', 'log1p', 'log2', 'log10',
    'pow', 'sqrt', 'acos', 'asin', 'atan', 'atan2', 'cos', 'hypot', 'sin', 'tan', 'degrees', 'radians', 
    'max', 'min', 'sum', 'any', 'all', 'not',
    ]

    allowed_constants = [
    'pi','tau','avo',
    ]

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
    def notf(arg): return not arg

class PatternHook(object):
    # this class handles match expressions and match counts
    
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
    allowed_functions = ['count','exists','nexists']

    def __init__(self,h,p):
        self.expression_hook = h
        self.pattern_hook = p

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
    


