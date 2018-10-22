from textx import *

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
