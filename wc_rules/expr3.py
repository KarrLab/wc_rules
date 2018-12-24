from lark import Lark, tree, Transformer,Visitor, v_args
from pprint import pformat, pprint
# DO NOT USE CAPS
grammarparts = []

#  directives
grammarparts.append("""
%import common.WS
%import common.CNAME
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%ignore WS

COMMENT: /#.*/
%ignore COMMENT
""")

# defining an atom
grammarparts.append("""
    ?true: /True/
    ?false: /False/
    ?number: SIGNED_NUMBER
    ?string: ESCAPED_STRING

    ?literal: true|false|number|string

    variable: CNAME
    ?atom:
        | literal
        | match_expression
        | match_function_call
        | boolean_function_call 
        | variable_function_call
        | math_function_call
        | variable_attrget
        | variable
        | "(" arithmetic_expression ")"
        
""")

# variable attrget
grammarparts.append("""
    attribute: CNAME
    variable_attrget: variable "." attribute
""")

# variable functioncall
grammarparts.append("""
    variable_funcname: CNAME
    function_variable: CNAME
    ?kwargpair: function_variable "=" atom 
    ?kwargs: "(" [kwargpair ("," kwargpair)* ] ")"
    variable_function_call: variable "." variable_funcname kwargs
""")

# math functioncall
grammarparts.append("""
    math_funcname: CNAME
    ?args: atom ("," atom)*
    math_function_call: math_funcname "(" [args] ")"
""")
# pattern matching
grammarparts.append("""
    pattern: CNAME
    pattern_variable: CNAME
    varpair: pattern_variable ":" variable
    varpairs: "{" varpair ("," varpair)* "}"
    positive_match_statement:  varpairs "in" pattern
    negative_match_statement:  varpairs "not" "in" pattern
    ?match_expression: positive_match_statement
        | negative_match_statement
    match_function_call: "count(" positive_match_statement ")" -> count
""")

# arithmetic expression
# adapted from https://github.com/lark-parser/lark/blob/master/examples/python3.lark
grammarparts.append("""
    ?arithmetic_expression: term (add_op term)*
    ?term: factor (mul_op factor)*
    ?factor: atom | factor_op factor
    
    add_op: "+" -> add | "-" -> subtract
    mul_op: "*" -> multiply | "/" -> divide
    factor_op: "+" | "-" -> flipsign
""")

# assignment
grammarparts.append("""
    assigned_variable: CNAME
    assignment: assigned_variable "=" atom
""")

# boolean expression
grammarparts.append("""
    ?compare_op: ">=" -> geq 
        | ">" -> ge
        | "<=" -> leq
        | "<" -> le
        | "==" -> eq
        | "!=" -> ne
    boolean_expression: arithmetic_expression compare_op arithmetic_expression -> comparebool
        | arithmetic_expression -> defaultbool
        | boolean_function_call

    ?boolean_expression_list: boolean_expression ("," boolean_expression)*
    boolean_function_call: "any(" boolean_expression_list ")" -> any
        | "all(" boolean_expression_list ")" -> all
        | "not(" boolean_expression ")" -> not
""")

# defining entry point
grammarparts.append("""
    expression: assignment | boolean_expression
    expressions: expression*
    start:expressions
""")

grammar = "\n".join(grammarparts)
parser = Lark(grammar, start='start')

@v_args(inline=True)
class DependencyTransform(Transformer):

    def __init__(self,*args,**kwargs):
        self.variables = set()

    def variable(self,v):
        self.variables.add(str(v))

    def start(self,*expr):
        return self.variables