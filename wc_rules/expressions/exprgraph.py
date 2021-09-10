from .exprgraph_utils import ExprBase, StringToken, dfs_iter, dfs_visit, dfs_print, collect_elements, order_elements 
from .builtins import ordered_builtins
from ..utils.collections import subdict, grouper
from ..schema.base import BaseClass
from ..schema.attributes import *
from .parse import Token
from .parse import CONTAINS_STRINGTOKENS, LITERALS, ORDERED_OPERATORS, GROUP_BY_LEADERS

from functools import partial
from collections import defaultdict

# READ THIS BEFORE CODING NEW METHODS
# dfs_make iterates depth-wise through an expression tree (output of lark parser)
#	and creates a parallel obj_tables graph using Expr nodes
# when dfs_make encounters a term with data=x, it calls make_x() if it exists,
# else it returns a default Expr node
# make_x methods must have the interface:
# def make_x(children):
#	return Expr()

class Expr(ExprBase):
	order = IntegerAttribute()
	children = OneToManyAttribute(ExprBase,related_name='parents')
	assignment = BooleanAttribute()
	
class PatternReference(Expr):
	pattern_id = StringAttribute()

class FunctionReference(Expr):

	variable = StringAttribute()
	attribute = StringAttribute()
	subvariable = StringAttribute()
	function_name = StringAttribute()
	_source = ManyToOneAttribute(BaseClass,related_name='_targets')
	
	def variable_reference(self):
		if self.subvariable is not None:
			return f'{self.variable}.{self.subvariable}'
		return self.variable
		
	def attach_source(self,source):
		self.variable = None
		self.subvariable = None
		self.safely_add_edge('_source',source)
		return self


class Arg(Expr):
	keyword = StringAttribute()

class GroupTerm(Expr):
	# used for addition/subtraction, which is a list of +/- terms
	# used for multiplication/division, which is a list of *// terms
	prefix = StringAttribute()

class Literal(Expr):
	value = StringAttribute()

def make_literal(data,children=[]):
	if children:
		return Literal(data=data,value=children[0].value)
	return Literal(data=data)

for x in LITERALS:
	globals()[f'make_{x}'] = partial(make_literal,data=x)

def make_assignment(children):
	# get the declared variable from child0 and assign it as id to child1
	child0, child1 = children
	child1.id, child1.assignment = collect_elements([child0])['declared_variable'], True
	return child1

def make_function_call(children):
	contents,args = collect_elements(children), []
	fref = FunctionReference(**subdict(contents,CONTAINS_STRINGTOKENS,ignore=True))
	for arg in contents.get('args',[]):
		args.append(Arg(children=arg.children))
	if fref.variable is not None or fref.function_name in ordered_builtins:
		args = order_elements(args)
	for kwarg in contents.get('kwargs',[]):
		kw, arg = kwarg.children
		args.append(Arg(keyword=kw.children[0].value,children=arg.children))
	children = [fref] + args
	return Expr(data='function_call',children=children)

def make_boolean_expression(children):
	assert len(children)==3
	if children[1].data in ORDERED_OPERATORS:
		order_elements(children)
	return Expr(data='boolean_expression',children=children)

def group_by_leaders(data,children):
	assert len(children) % 2 == 0
	groupterms = defaultdict(lambda: GroupTerm(prefix=data))
	for leader,follower in grouper(children,2):
		groupterms[leader.data].children.add(follower)
	return Expr(data=data,children=list(groupterms.values()))

for x in GROUP_BY_LEADERS:
	globals()[f'make_{x}'] = partial(group_by_leaders,data=x)

def dfs_make(tree):
	if isinstance(tree,Token):
		return StringToken(value=str(tree))
	data, children = tree.data, [dfs_make(x) for x in tree.children]
	if f'make_{data}' in globals():
		fn = globals()[f'make_{data}']
		return fn(children=children)
	return Expr(data=data,children=children)
