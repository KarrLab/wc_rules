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

    ?number: NUMBER
    ?atom: "(" sum ")" | number | function_call

    function_name: CNAME
    variable: CNAME
    attribute: CNAME

    arg: expression
    kw: CNAME
    kwarg: kw "=" arg
    ?argkwarg: arg | kwarg
    ?argkwargs: argkwarg ("," argkwarg)*

    function_call: variable "." function_call
        | variable
        | function_name "(" [argkwargs] ")"

    ?sum: term (add_op term)*
    ?term: factor (mul_op factor)* 
    ?factor: factor_op factor | atom

    ?factor_op: "+" | "-" -> flipsign
    ?add_op: "+" -> add | "-" -> subtract
    ?mul_op: "*" -> multiply | "/" -> divide    

    ?expression: sum
    expressions: expression*
    start:expressions
"""

parser = Lark(grammar, start='start')
