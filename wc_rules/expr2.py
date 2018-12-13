from lark import Lark, tree, Transformer
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
    literal: "True" -> true 
        | "False" -> false 
        | SIGNED_NUMBER -> number 
        | ESCAPED_STRING -> string

    variable: CNAME
    ?atom:
        | boolean_function_call 
        | variable_function_call
        | math_function_call
        | variable_attrget
        | variable
        | literal
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


# arithmetic expression
# adapted from https://github.com/lark-parser/lark/blob/master/examples/python3.lark
grammarparts.append("""
    arithmetic_expression: term (add_op term)*
    ?term: factor (mul_op factor)*
    ?factor: factor_op factor | atom
    
    add_op: "+" -> add | "-" -> subtract
    mul_op: "*" -> multiply | "/" -> divide
    factor_op: "+" | "-" -> flipsign
""")

# boolean expression
grammarparts.append("""
    compare_op: ">=" -> geq 
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
    ?expression: boolean_expression
    expressions: expression*
""")

grammar = "\n".join(grammarparts)

parser = Lark(grammar, start='expressions')

dummytext = '''
any(-(--a + b*4/5*-6) + "Strsdf", baba>0)
a.x  
a.get_sequence(a=b,x=c)
a.get_sequence()== any(x.a, y.b)
pow(a,x.y)
'''

#print(parser.parse(dummytext).pretty())
