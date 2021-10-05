from ..schema.base import BaseClass
from ..schema.attributes import StringAttribute
from lark import Token

class ExprBase(BaseClass):
	data = StringAttribute()

	def serialize_for_vis(self):
		d = self.get_literal_attrdict()
		return '\n'.join([f'{k}:{v}' for k,v in d.items()])

class StringToken(ExprBase):
	value = StringAttribute()


def dfs_iter(tree):
	return [tree] + merge_lists([dfs_iter(x) for x in getattr(tree,'children',[])])

def dfs_visit(tree,ignore_tokens=True):
	yield tree
	if hasattr(tree,'children'):
		for child in tree.children:
			for elem in dfs_visit(child):
				ignore = ignore_tokens and isinstance(elem,Token)
				if not ignore:
					yield elem

def dfs_print(tree,tab_level=0):
	tabs = str(tab_level) + ' '*(tab_level+1)
	if isinstance(tree,Token):
		data, children = str(tree), []
		return f'{tabs}{data}'
	
	data = tree.data
	children = (dfs_print(x,tab_level=tab_level+1) for x in getattr(tree,'children',[]))
	children = '\n'.join(children)
	return f'{tabs}{data}\n{children}'

def collect_elements(elems):
	d = {}
	for elem in elems:
		if len(elem.children) == 1 and isinstance(elem.children[0],StringToken):
			d[elem.data] = elem.children[0].value
		else:
			d[elem.data] = elem.children
	return d	

def order_elements(elems):
	for i,elem in enumerate(elems):
		elem.order = i
	return elems