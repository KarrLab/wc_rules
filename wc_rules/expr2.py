from lark import Lark, tree, Transformer,Visitor, v_args
from collections import defaultdict
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

    ?boolean_expression: expression bool_op expression
        | match_expression 
        | expression
    
    ?bool_op: ">=" -> geq | "<=" -> leq | ">" -> ge | "<" -> le | "==" -> eq | "!=" -> ne
    
    pattern: CNAME
    pattern_variable:CNAME
    varpair: pattern_variable ":" variable
    varpairs: varpair ("," varpair)*
    match_expression: "{" varpairs "}" "in" pattern
    match_count: "count" "(" match_expression ")"

    assignment: declared_variable "=" (expression|boolean_expression)
    declared_variable: CNAME

    expressions: (assignment|boolean_expression) (NEWLINE (assignment|boolean_expression))* 
    ?start: [NEWLINE] expressions [NEWLINE]
"""

parser = Lark(grammar, start='start')

def node_to_str(node):
    return node.children[0].__str__()

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