from lark import Lark, tree, Transformer,Visitor, v_args, Tree,Token
from .utils import merge_lists, merge_dicts, pipe_map,listmap
from operator import itemgetter,attrgetter
from functools import partial


action_grammar = """
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
    ?atom: literal | function_call  | "(" expression ")" 

    function_name: CNAME
    attribute: CNAME
    declared_variable: CNAME
    pattern: CNAME
    node: CNAME

    arg: expression
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

    ?factor_op: "+" -> noflip | "-" -> flipsign
    ?add_op: "+" -> add | "-" -> subtract
    ?mul_op: "*" -> multiply | "/" -> divide    

    ?expression: sum

    boolean_expression: expression bool_op expression
    
    ?bool_op: ">=" -> geq | "<=" -> leq | ">" -> ge | "<" -> le | "==" -> eq | "!=" -> ne
    
    assignment: declared_variable "=" (expression|boolean_expression)

    action_name: CNAME
    action: variable "." attribute "." action_name "(" [atom] ")"
    
    ?start: (assignment|boolean_expression)
"""    
    #expressions: (assignment|boolean_expression) (NEWLINE (assignment|boolean_expression))* 
    #?start: [NEWLINE] expressions [NEWLINE]



parser = Lark(action_grammar, start='start')

