from textx import *
from .utils import ParseExpressionError

is_empty_grammar = '''
Expression:
    variable=ID '.' attribute=ID 'empty' ;
'''
is_empty_parser = metamodel_from_str(is_empty_grammar,autokwd=True)

is_in_grammar = '''
Expression:
    variable=ID is_not?='not' 'in' varloc=VariableLocation;
VariableLocation:
    pattern=ID '.' variable=ID ;
'''
is_in_parser = metamodel_from_str(is_in_grammar,autokwd=True)

is_in_list_grammar = '''
Expression:
    lhs=VariableList is_not?='not' 'in' pattern=ID '.' rhs=VariableList;
VariableList:
    '[' variables+=ID[','] ']' | variables=ID ;
'''
is_in_list_parser = metamodel_from_str(is_in_list_grammar,autokwd=True)


bool_cmp_simple_grammar = '''
Expression:
    is_not?='!' variable=ID '.' attribute=ID ;
'''
bool_cmp_simple_parser = metamodel_from_str(bool_cmp_simple_grammar)

bool_cmp_complex_grammar = '''
Expression2:
    variable=ID '.' attribute=ID op=Compare value=BOOL;
Compare:
    '==' | '!=' ;
'''
bool_cmp_complex_parser = metamodel_from_str(bool_cmp_complex_grammar)

num_cmp_grammar = '''
Expression:
    variable=ID '.' attribute=ID op=Compare value=NUMBER ;
Compare:
    '==' | '!=' | '>' | '<' | '>=' | '<=' ;
'''

num_cmp_parser = metamodel_from_str(num_cmp_grammar)



def parse_expression(string_input):
    # Step 1: is_empty
    expr = use_parser(string_input,is_empty_parser)
    if expr is not None:
        tup = (expr.variable, expr.attribute)
        return 'is_empty', tup

    # Step 2: is_in and is_not_in
    expr = use_parser(string_input,is_in_list_parser)
    if expr is not None:
        var_lhs = tuple(expr.lhs.variables)
        var_rhs = tuple(expr.rhs.variables)
        pattern = expr.pattern
        tup = (var_lhs,pattern,var_rhs)
        if expr.is_not:
            return 'is_not_in',tup
        else:
            return 'is_in',tup

    # Step 4: bool_cmp
    expr = use_parser(string_input,bool_cmp_simple_parser)
    if expr is not None:
        if expr.is_not:
            return 'bool_cmp', (expr.variable,expr.attribute,'!=', True)
        else:
            return 'bool_cmp', (expr.variable,expr.attribute,'==', True)

    expr = use_parser(string_input,bool_cmp_complex_parser)
    if expr is not None:
        d = {'!=':'==','==':'!='}
        if expr.value is False:
            return 'bool_cmp', (expr.variable,expr.attribute,d[expr.op], True)
        else:
            return 'bool_cmp', (expr.variable,expr.attribute,expr.op, True)

    # Step 5: num_cmp
    expr = use_parser(string_input,num_cmp_parser)
    if expr is not None:
        return 'num_cmp', (expr.variable,expr.attribute,expr.op,expr.value)

    raise ParseExpressionError('Could not parse expression! ' + string_input)
    return None,None

def use_parser(string_input,parser):
    try:
        model = parser.model_from_str(string_input)
    except:
        model = None
    return model
