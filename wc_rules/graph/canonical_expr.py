from .expr import process_expression_string
from .base import BaseClass
from .attributes import StringAttribute, OneToOneAttribute, ManyToManyAttribute, OneToManyAttribute
from .indexer import GraphContainer
from .utils import generate_id, listmap, pipe_map, grouper, merge_lists, invert_dict, tuplify_dict
from .executable_expr import ordered_builtins
from .canonical import *
from operator import itemgetter
from collections import defaultdict


class ExprBase(BaseClass):
	pass

class Expr(ExprBase):
	# generic node on the tree
	data = StringAttribute()
	children = ManyToManyAttribute(ExprBase,related_name='parents')

class Variable(Expr):
	def __init__(self,name):
		super().__init__(name)

class Root(Expr):
	def __init__(self,children):
		super().__init__('_root',children=listmap(Variable,children))

def dfs_make(tree):
	if isinstance(tree,str):
		return Expr(data=str(tree))
	if tree.data == 'args':
		return unordered_args(tree)
	if tree.data in ['sum','term']:
		return group_by_leaders(tree)
	if tree.data == 'boolean_expression':
		return boolean_expression(tree)
	if (tree.data=='function_call') and getattr(tree.children[0],'data','') == 'function_name':
		return builtin_function_call(tree)
	

	children = listmap(dfs_make,getattr(tree,'children',[]))
	return Expr(data=tree.data,children=children)

def group_by_leaders(tree):
	# takes tree(data,children = ['add', x, 'add', y, 'subtract', z])
	# returns Expr(data,[Expr('add',[x,y]), Expr('subtract',[z])])
	elems = defaultdict(list)
	for leader,child in grouper(2,tree.children):
		elems[leader.data].append(dfs_make(child))	
	children = [Expr(data=k,children=v) for k,v in elems.items()]
	return Expr(data=tree.data,children=children)

def nest_within(_dict):
	return [Expr(data=k,children=[v]) for k,v in _dict.items()]

def boolean_expression(tree):
	lhs, op, rhs = listmap(dfs_make,tree.children)
	if op.data in ['eq','ne']:
		return Expr(data='boolean_expression',children=[op,lhs,rhs])
	new_lhs, new_rhs = nest_within({'lhs':lhs,'rhs':rhs})
	return Expr(data='boolean_expression',children=[op,new_lhs,new_rhs])

def unordered_args(tree):
	children = [arg.children[0] for arg in tree.children]
	return Expr(data='args',children=listmap(dfs_make,children))

def builtin_function_call(tree):
	elems = listmap(dfs_make,getattr(tree,'children',[]))
	if len(elems)==2:
		fname = elems[0].children[0].data
		if fname in ordered_builtins:
			children = nest_within(dict(zip(['arg01','arg02'],elems[1].children)))
			elems[1] = Expr(data='args',children=children)			
	return Expr(data=tree.data,children=elems)
	

def dfs_iter(tree):
	return [tree] + merge_lists([dfs_iter(x) for x in getattr(tree,'children',[])])

def dfs_filter(tree,predicate):
	return [x for x in dfs_iter(tree) if predicate(x)]

def dfs_print(tree,tab_level=0):
	children = (dfs_print(x,tab_level=tab_level+1) for x in getattr(tree,'children',[]))
	return '{tabs}{data}\n{children}'.format(
		tabs = str(tab_level) + ' '*(tab_level+1),
		data = tree.data,
		children = '\n'.join(children)
		)

def constraint_to_tree(var,constraint):
	larktree,_ = process_expression_string('{v} = {c}'.format(v=var,c=constraint.code))
	tree = dfs_make(larktree)
	return tree

def namespace_to_graph(namespace):
	root = Root(namespace)
	g = GraphContainer(root.get_connected())
	return g

def replace_node(source,target):
	parents = source.parents
	for parent in parents:
		parent.children.remove(source)
		parent.children.add(target)
	return

def add_tree_to_g(g,tree):
	var_nodes = dfs_filter(tree,lambda x: x.data in ['variable','declared_variable'])
	for node in var_nodes:
		varname = node.children[0].data
		replace_node(node,g[varname])
	return

def canonical_expression_ordering(seed,namespace,constraints):
	g = namespace_to_graph(namespace)
	trees = [constraint_to_tree(var,c) for var,c in constraints.items()]
	for tree in trees:
		add_tree_to_g(g,tree)
	g.update()
	# partition_namespace(seed,namespace)
	partition, order, leaders = canonical_ordering(g,seed)
	
	final_elems = concat(seed)
	partition = tuple([tuple(x) for x in partition if x[0] in final_elems])
	leaders = tuple([tuple(x) for x in leaders if x[0] in final_elems])
	
	return partition, leaders



def initial_partition(nodes,g):
	return deque( group_by_node_certificates(initial_exprnode_certificate, nodes, g=g) )

# def initial_exprnode_certificate(idx,g):
# 	return (-g[idx].degree(), getattr(g[idx],'data',''))

def initial_exprnode_certificate(idx,g):
	x = g[idx]
	degree = x.degree()
	classname = x.__class__.__name__
	attrs = tuplify_dict(x.get_literal_attrdict(ignore_id=True))
	return (-degree,classname,attrs)


def partition_namespace(seed,namespace):
	# helpervar: helperpattern
	# constraintvar: constraint/assignment str
	# graphvar: descendent of baseclass
	d = {(True,False):'node',(False,True):'constraint',(False,False):'helper'}
	def what_type(x): 
		return d[isinstance(x,type),isinstance(x,str)]
	d2 = invert_dict({x:what_type(y) for x,y in namespace.items()})

	assert sorted(merge_lists(seed)) == sorted(d2['node']), 'Fails check in partitioning namespace.'
	
	seed = [list(x) for x in seed]
	helpers = sorted(d2.get('helper',[]))
	assignments = sorted([x for x in d2.get('constraint',[]) if x[0]!='_'])
	conditions = sorted([x for x in d2.get('constraint',[]) if x[0]=='_'])
	partition = concat([seed,[helpers],[assignments],[conditions]])
	
	return partition