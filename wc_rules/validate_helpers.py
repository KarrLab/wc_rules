from collections import Counter
from .utils import all_unique, check_cycle
from keyword import iskeyword

def validate_class(_obj,classes,prefix):
	err = "{0} must be an instance of {1}"
	assert isinstance(_obj,classes), err.format(prefix,classes)

def validate_dict(_dict,classes,prefix):
	for k,v in _dict.items():
		validate_class(v,classes,'{0} {1}'.format(prefix,k))

def validate_list(_list,classes,prefix):
	for elem in _list:
		validate_class(elem,classes,'{0} {1}'.format(prefix,elem))

def validate_set(_list,prefix):
	err = "{0} must be unique."
	assert len(_list) == len(set(_list)), err.format(prefix)

def validate_unique(master,child,prefix):
	for x in child:
		err = "`{0}` for {1} as it already exists in the namespace."
		assert x not in master, err.format(x,prefix)

def validate_contains(master,child,prefix):
	for x in child:
		err = "{0} named `{1}` does not exist."
		assert x in master, err.format(prefix,x)

def validate_acyclic(kwdeps):
	cycle = check_cycle(kwdeps)
	err = "Cyclical dependency found: {0}."
	assert len(cycle)==0, err.format(cycle)

def validate_keywords(_list,prefix):
	for x in _list:
		err = "`{0}` is not a valid {1} name."
		assert isinstance(x,str) and x.isidentifier() and not iskeyword(x), err.format(x,prefix)

def validate_literal_attribute(node,attr):
	node.__class__.Meta.attributes[attr].check_value(node.get(attr))
	
def validate_literal_attributes(node):
	for attr in node.get_literal_attributes(ignore_id=False,ignore_None=True):
		validate_literal_attribute(node,attr)

def validate_related_attribute(node,attr):
	x = node.__class__.Meta.local_attributes[attr]
	classes = node.get_related_class(attr)
	targets = node.listget(attr)
	for target in targets:
		validate_class(target,classes,'Target of related attribute {0} of class {1}'.format(attr,node.__class__))

	# validate only max
	if x.is_primary:
		max_related = node.__class__.Meta.attributes[attr].max_related
	else:
		max_related = targets[0].__class__.Meta.attributes[node.get_related_name(attr)].max_related_rev
	err = 'Targets of related attribute {0} of class {1} exceed max_related value {2}'
	assert len(node.listget(attr)) <= max_related, err.format(attr,node.__class__,max_related)

def validate_related_attributes(node):
	for attr in node.get_related_attributes(ignore_None=True):
		validate_related_attribute(node,attr)


def validate_namespace(*args):
	c = Counter()
	for arg in args:
		c.update(arg)
	duplicates = [x for x in c if c[x]>2]