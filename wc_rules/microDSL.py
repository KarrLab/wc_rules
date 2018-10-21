from textx import *

is_empty_grammar = '''
Expression: variable=ID '.' attribute=ID 'is_empty' ;
'''
is_empty_parser = metamodel_from_str(is_empty_grammar,autokwd=True)
