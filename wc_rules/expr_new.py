from lark import Lark, tree, Transformer,Visitor, v_args, Tree,Token
from .utils import merge_lists, merge_dicts, pipe_map,listmap
from operator import itemgetter,attrgetter
from functools import partial


grammar = """
%import common.CNAME
%import common.WS_INLINE
%import common.NUMBER
%ignore WS_INLINE
%import common.ESCAPED_STRING
%import common.NEWLINE

COMMENT: /#.*/
%ignore COMMENT
%ignore NEWLINE

    ?literal.1: NUMBER -> number | "True"-> true | "False" -> false | ESCAPED_STRING -> string
    ?atom: literal | function_call | "(" expression ")" 

    function_name: CNAME
    variable: CNAME
    attribute: CNAME

    arg: expression
    kw: CNAME
    kwarg: kw "=" arg
    args: arg ("," arg )*
    kwargs: kwarg ("," kwarg)*
    
    function_call: variable "." function_name "(" [kwargs] ")"
        | function_name "(" [args] ")"
        | variable "." attribute 
        | variable
        
    ?sum: term (add_op term)*
    ?term: factor (mul_op factor)* 
    ?factor: factor_op factor | atom

    ?factor_op: "+" -> noflip | "-" -> flipsign
    ?add_op: "+" -> add | "-" -> subtract
    ?mul_op: "*" -> multiply | "/" -> divide    

    ?expression: sum

    boolean_expression: expression bool_op expression
    
    ?bool_op: ">=" -> geq | "<=" -> leq | ">" -> ge | "<" -> le | "==" -> eq | "!=" -> ne
    
    assignment: declared_variable "=" (expression|boolean_expression)
    declared_variable: CNAME

    expressions: (assignment|boolean_expression) (NEWLINE (assignment|boolean_expression))* 
    ?start: [NEWLINE] expressions [NEWLINE]
"""


parser = Lark(grammar, start='start')

### process constraint string
def process_constraint_strings(string_input):
    #### This is the main method
    # parses a string input to generate a tree, prunes new lines,
    # simplifies based on basic arithmetic,
    # analyzes dependencies,
    
    # parse string input to generate a tree
    tree = parser.parse(string_input)
    # prune newline tokens
    nodes = list(filter(lambda x:x.__class__.__name__=='Token',tree.children))
    for node in list(nodes):
        tree.children.remove(node)

    # simplify the tree
    tree,modified = simplify_tree(tree) 
    
    deps = Dependency_Analyzer().transform(tree=tree)
    return tree,deps



def simplify_tree(tree): 
    '''
    # PURPOSE: simplify and standardize expressions using arithmetic rules
    # Rules for simplification
    # parent ->factor -> noflip,item ==> parent -> item AKA +x ==> x
    # parent ->factor1 -> flipsign,factor2 -> flipsign,item  ==> parent->item AKA --x ==> x
    # parent -> multiply,term -> items ==> parent -> items AKA x*(y*z) ==> x*y*z
    # parent -> divide,term -> items ==> parent -> flipped(items) AKA 1/(/(x)) ==> x
    # sum -> add,sum -> items ==> sum -> items AKA x+(y+z) ==> x+y+z
    # sum -> subtract,sum -> items ==> sum -> flipped(items) AKA x-(y+z) ==> x-y-z
    '''
    def node_to_str(node):
        return node.children[0].__str__()

    def find_parents_of(tree,data):
        f = lambda t: any([getattr(x,'data','')==data for x in t.children])
        return tree.find_pred(f)    

    # here, we reshape and simplify the tree
    modified = False
    
    # find parent->factor->noflip,item
    # replace with parent->item
    # e.g., +x to x
    nodes = find_parents_of(tree,'factor')
    for node in nodes:
        # get their factor children that have noflip children
        factors = [x for x in node.children 
            if getattr(x,'data','')=='factor'
            and x.children[0].data=='noflip'
            ]
        modified = modified or len(factors)>0
        for factor in factors:
            ind = node.children.index(factor)
            node.children[ind] = factor.children[1]

    # find parent->factor1->flipsign,factor2->flipsign,item
    # replace with parent->item
    # e.g., --x to x
    nodes = find_parents_of(tree,'factor')
    ignored = []
    for node in nodes:
        if node in ignored:
            continue
        factors = [x for x in node.children 
            if getattr(x,'data','')=='factor'
            and x.children[0].data=='flipsign'
            and x.children[1].data=='factor'
            and x.children[1].children[0].data =='flipsign'
            ]
        modified = modified or len(factors)>0
        for factor in factors:
            ignored.append(factor.children[1])
            ind = node.children.index(factor)
            node.children[ind] = factor.children[1].children[1]

    # insert 'multiply' as first item in all data=='term'
    nodes = list(tree.find_data('term'))
    for node in nodes:
        if getattr(node.children[0],'data','') not in ['multiply','divide']:
            node.children.insert(0,Tree(data='multiply',children=[]))

    # identify parent -> multiply, term -> items 
    # replace with parent -> items
    # identify parent -> divide,term -> items
    # replace with parent -> flipped(items)
    collapsible = False
    for node in nodes:
        for i in range(len(node.children)-1):
            if getattr(node.children[i],'data','')=='multiply' and getattr(node.children[i+1],'data','')=='term':
                collapsible = True
                insert_this = node.children[i+1].children
            if getattr(node.children[i],'data','')=='divide' and getattr(node.children[i+1],'data','')=='term':
                collapsible = True
                insert_this = []
                for term in node.children[i+1].children:
                    if getattr(term,'data','')=='multiply':
                        insert_this.append(Tree(data='divide',children=[]))
                    elif getattr(term,'data','')=='divide':
                        insert_this.append(Tree(data='multiply',children=[]))
                    else:
                        insert_this.append(term)
            if collapsible:
                del node.children[i:i+2]
                node.children[i:i] = insert_this
                break
        if collapsible:
            break
    modified = modified or collapsible

    #first insert 'add' as first token of sums
    nodes = list(tree.find_data('sum'))
    for node in nodes:
        if getattr(node.children[0],'data','') not in ['add','subtract']:
            node.children.insert(0,Tree(data='add',children=[]))
    # find sum -> add, sum -> items
    # replace with sum -> items
    # e.g., x + (y+z) to x + y + z
    # find sum -> subtract, sum -> items
    # replace with sum -> flipped(items)
    # e.g., x - (y+z) to x - y - z
    collapsible = False
    for node in nodes:
        for i in range(len(node.children)-1):
            if getattr(node.children[i],'data','')=='add' and getattr(node.children[i+1],'data','')=='sum':
                collapsible = True
                insert_this = node.children[i+1].children
            if getattr(node.children[i],'data','')=='subtract' and getattr(node.children[i+1],'data','')=='sum':
                collapsible = True
                insert_this = []
                for term in node.children[i+1].children:
                    if getattr(term,'data','')=='add':
                        insert_this.append(Tree(data='subtract',children=[]))
                    elif getattr(term,'data','')=='subtract':
                        insert_this.append(Tree(data='add',children=[]))
                    else:
                        insert_this.append(term)
            if collapsible:
                del node.children[i:i+2]
                node.children[i:i] = insert_this
                break
        if collapsible:
            break
    modified = modified or collapsible

    # find sum -> subtract,factor->flipsign,item
    # replace with sum -> add, item
    # e.g., x - (-y) + z to x + y + z
    nodes = list(tree.find_data('sum'))
    for node in nodes:
        subtract_index = [
        i for i,x in enumerate(node.children)
            if getattr(x,'data','')=='subtract'
            and getattr(node.children[i+1],'data','')=='factor'
            and getattr(node.children[i+1].children[0],'data','')=='flipsign'
            ]

        modified = modified or len(subtract_index)>0
        for i in subtract_index:
            item = node.children[i+1].children[1]
            node.children[i] = Tree(data='add',children=[])
            node.children[i+1] = item

    return (tree,modified)


class Dependency_Analyzer(Transformer):
    '''
    # PURPOSE:
    # Analyzes a tree for dependencies
    # Returns a list, with length equal to number of constraints
    # Each element is a nested list, with each item a dictionary or nested list
    # Dictionaries hold information on variables, attributes, function calls, declared variables
    # 'arg' attribute of dictionary is a nested list 
    '''

    # literals and operators, return None
    def return_None(x,y): return None
    number = string = true = false = return_None
    geq = leq = ge = le = ne = eq = return_None
    flipsign = subtract = add = multiply = divide = return_None

    def return_list_minus_None(x,y): return [i for i in y if i is not None]

    # these terms return nested lists, eliminating None terms
    sum = term = factor = return_list_minus_None
    boolean_expression = return_list_minus_None
    arg = kwarg = return_list_minus_None
    assignment = return_list_minus_None

    def return_dict(keyword): return lambda x,y: {keyword:y[0].__str__()}

    # these terms return dicts
    variable = return_dict('variable')
    declared_variable = return_dict('declared_variable')
    attribute = return_dict('attribute')
    function_name = return_dict('function_name')
    kw = return_dict('kw')

    def args(x,y): 
        # joins a list of lists
        #return dict(args=list(chain(*y)))
        return dict(args = merge_lists(y))

    def kwargs(x,y):
        # joins list of lists of args
        # plucks and joins keywords
        args = merge_lists(map(itemgetter(1),y))
        kws = list(pipe_map([itemgetter(0),itemgetter('kw')], y))
        return dict(kws=kws,args=args)
        
    def function_call(x,y):
        return merge_dicts(y)
        
    # this returns a nested list, with possible empty entries
    def return_list(x,y): return y
    expressions = return_list
        
    
