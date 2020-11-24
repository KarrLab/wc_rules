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


    LITERAL.1: NUMBER | "True" | "False" | ESCAPED_STRING
    SYMBOL:  "==" | "!=" |"<="| ">=" | "<" | ">" | "=" | "," | "+" | "-" | "*" | "/" | "." | "(" | ")"

    variable.1: CNAME
    subvariable: CNAME
    attribute: CNAME    
    action_name: CNAME
    GRAPH_ACTION_NAME: "add" | "remove" | "set"
    
    ?graph_target.1: variable ["." subvariable]
    arg:  graph_target | LITERAL  | expression
    args: arg ("," arg)*
    graph_action.2: variable ["." subvariable]  "." GRAPH_ACTION_NAME ["_" attribute] "(" [args] ")"
    
    kw: CNAME
    kwarg: kw "=" arg
    kwargs: kwarg ("," kwarg)* 
    custom_action: variable ["." subvariable] "." action_name "(" [kwargs] ")"

    ?action.1: graph_action|custom_action

    expression: (LITERAL | SYMBOL | CNAME )+ 
    ?start: action | expression


"""
# args: arg ("," arg)*


    #expressions: (assignment|boolean_expression) (NEWLINE (assignment|boolean_expression))* 
    #?start: [NEWLINE] expressions [NEWLINE]



parser = Lark(action_grammar, start='start')

