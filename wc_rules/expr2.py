from lark import Lark, tree, Transformer,Visitor, v_args
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
        | variable "." attribute 
        | variable
        
    ?sum: term (add_op term)*
    ?term: factor (mul_op factor)* 
    ?factor: factor_op factor | atom

    ?factor_op: "+" | "-" -> flipsign
    ?add_op: "+" -> add | "-" -> subtract
    ?mul_op: "*" -> multiply | "/" -> divide    

    ?expression: sum

    boolean_expression: expression bool_op expression
        | match_expression 
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

def preprocess_tree(tree): return tree

def get_dependencies(tree):
    deplist = []
    for expr in tree.children:
        if not hasattr(expr,'data'):
            # this is to ignore NEWLINE tokens at the top level
            continue
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
                deps['varfunctions'].add( (var,func) )
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

    def __init__(self,h,p):
        self.expression_hook = h
        self.pattern_hook = p

    def join_strings(self,args): return " ".join(args)
    def constant(s): return lambda x,y: s
    def n2s(self,arg): return arg[0].__str__()

    
    def expressions(self,args):
        return [x for x in args if x.__class__.__name__ != 'Token']
    

    def function_call(self,args):
        names = []
        arglist = []
        is_a_function = False
        if args[0].data == 'variable':
            names.append('m')
            names.append(self.n2s(args[0].children)) 
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
            names.append(self.n2s(args[0].children))
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
    
    
    boolean_expression = list
    


