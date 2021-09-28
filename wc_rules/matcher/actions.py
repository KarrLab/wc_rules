from frozendict import frozendict

def make_node_token(_class,idx,action):
	return frozendict(dict(_class=_class,idx=idx,action=action))

def make_edge_token(_class1,idx1,attr1,idx2,attr2,action):
	return frozendict(dict(_class=_class1,idx1=idx1,idx2=idx2,attr2=attr2,action=action))	

def make_attr_token(_class,idx,attr,value,action):
	return frozendict(dict(_class=_class,idx=idx,attr=attr,value=value,action=action))	

def make_cache_token(variables,values,action):
	return frozendict(variables=variables,values=values,action=action)


