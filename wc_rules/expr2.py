from lark import Lark, tree, Transformer
# DO NOT USE CAPS
grammar = """
    variable: CNAME
    attribute: CNAME
    variable_attrget: variable "." attribute

    pattern: CNAME
    pattern_variable: CNAME
    variable_pair: pattern_variable ":" variable
    variable_pairs: "{" variable_pair ("," variable_pair)* "}"
    positive_match_expression: variable_pairs "in" pattern
    negative_match_expression: variable_pairs "not in" pattern
    count_match_expression: "count(" + positive_match_expression + ")"

    boolean_literal: "True" | "False"
    numeric_literal: SIGNED_NUMBER | boolean_literal | constant
    constant: "pi"->constant_pi | "e"->constant_e
    literal: numeric_literal | ESCAPED_STRING

    argument: variable|literal
    function_variable: CNAME
    argument_pair: function_variable "=" argument
    argument_pairs: "(" [ argument_pair ("," argument_pair)* ] ")"
    function_name: CNAME
    variable_function_call: variable "." function_name argument_pairs

    math_argument: variable|numeric_literal
    math_arguments:  "(" [ math_argument ("," math_argument)* ] ")"
    math_function_name: CNAME
    math_function_call: math_function_name math_arguments | numeric_literal

    ?basic_expression_unit: positive_match_expression
        | count_match_expression
        | negative_match_expression
        | variable_function_call
        | variable_attrget
        | math_function_call
        | "(" basic_expression_unit ")"

    ?numeric_expression_unit: basic_expression_unit | numeric_literal

    compare_op: ">=" -> geq
        | ">" -> ge
        | "<=" -> leq
        | "<" -> le
        | "==" -> eq
        | "!=" -> neq
    ?boolean_expression: numeric_expression_unit compare_op numeric_expression_unit
        | boolean_function_call
        | numeric_expression_unit

    boolean_expression_list: "(" boolean_expression [ ("," boolean_expression)* ] ")"
    boolean_funcname: "not" -> not| "any" ->any | "all" -> all
    boolean_function_call: boolean_funcname boolean_expression_list

    ?expression: basic_expression_unit | boolean_expression
    expressions: expression*

    %import common.WS
    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %ignore WS
"""

parser = Lark(grammar, start='expressions')

text = '''
{site:x} not in bonded
{site:x} not in overlapped
count({site:x} in phosphorylated)
a.get_sequence(start=0,end=end)
a.get_sequence()
a.x > 2
a.x == pi
not(a.x > pi, b.y < pi, any(c.z, d.p == False))

'''

print(parser.parse(text).pretty())
