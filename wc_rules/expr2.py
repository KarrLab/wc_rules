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
""")

# variable_attrget
grammarparts.append("""
    variable: CNAME
    attribute: CNAME
    variable_attrget: variable "." attribute
""")

# pattern matching
grammarparts.append("""
    pattern: CNAME
    pattern_variable: CNAME
    variable_pair: pattern_variable ":" variable
    variable_pairs: "{" variable_pair ("," variable_pair)* "}"
    positive_match_expression: variable_pairs "in" pattern
    negative_match_expression: variable_pairs "not in" pattern
    count_match_expression: "count(" + positive_match_expression + ")"
    ?match_expression: positive_match_expression
        | negative_match_expression
        | count_match_expression
""")

# variable function call
grammarparts.append("""
    function_name: CNAME
    function_variable: CNAME
    ?function_argument: basic_expression_unit
    function_argv: function_variable "=" function_argument
    function_argvlist: function_argv ("," function_argv)*
    variable_function_call: variable "." function_name "(" [function_argvlist] ")"
""")

# negation and bracketing
grammarparts.append("""
    ?bracketed_expression: "(" basic_expression_unit ")"
    negated_expression: "-" basic_expression_unit -> neg
""")

# literals
grammarparts.append("""
    BOOLEAN: "True" | "False"
    literal:
    | BOOLEAN -> bool
    | SIGNED_NUMBER -> num
    | ESCAPED_STRING -> string

""")

# expressions entry point
grammarparts.append("""
    ?basic_expression_unit:
        | variable
        | variable_attrget
        | match_expression
        | variable_function_call
        | bracketed_expression
        | negated_expression
        | literal
    expressions: basic_expression_unit*
""")

grammar = "\n".join(grammarparts)

parser = Lark(grammar, start='expressions')

text1 = '''
{site:x} not in bonded
{site:x} not in overlapped
count({site:x} in phosphorylated)
'''
text = '''
x.get_sequence(a=0,b=v)
x.get_sequence()
x.get_sequence(reverse= - {site:x} not in phosphorylated)
'''
