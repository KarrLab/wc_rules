from lark import Lark, tree, Transformer,Visitor, v_args
from pprint import pformat, pprint
# DO NOT USE CAPS
grammar = """
%import common.CNAME
%import common.WS
%import common.NUMBER
%ignore WS
%import common.ESCAPED_STRING
%ignore WS

COMMENT: /#.*/
%ignore COMMENT

    ?number.1: NUMBER -> number | "True"-> true | "False" -> false | ESCAPED_STRING -> string
    ?atom: number | function_call | "(" sum ")" 

    function_name: "any" -> anyfunc | "all" -> allfunc | "not" -> notfunc | CNAME
    variable: CNAME
    attribute: CNAME

    arg: expression
    kw: CNAME
    kwarg: kw "=" arg
    args: arg ("," arg )*
    kwargs: kwarg ("," kwarg)*
    
    function_call: variable "." function_name "(" [kwargs] ")"
        | function_name "(" [args] ")"
        | function_name "(" [boolargs] ")" 
        | match_count
        | variable "." attribute 
        | variable
        
    ?sum: term (add_op term)*
    ?term: factor (mul_op factor)* 
    ?factor: factor_op factor | atom

    ?factor_op: "+" | "-" -> flipsign
    ?add_op: "+" -> add | "-" -> subtract
    ?mul_op: "*" -> multiply | "/" -> divide    

    ?expression: sum

    boolean_expression: expression bool_op expression -> comparebool
        | match_expression -> matchbool
        | expression -> defaultbool


    ?bool_op: ">=" -> geq | "<=" -> leq | ">" -> ge | "<" -> le | "==" -> eq | "!=" -> ne
    boolargs: boolean_expression ("," boolean_expression)*
    
    pattern: CNAME
    pattern_variable:CNAME
    varpair: pattern_variable ":" variable
    varpairs: varpair ("," varpair)*
    match_expression: "{" varpairs "}" "in" pattern
    match_count: "count" "(" match_expression ")"

    assignment: variable "=" (expression|boolean_expression)

    expressions: (assignment|boolean_expression)*
    start:expressions
"""

parser = Lark(grammar, start='start')
