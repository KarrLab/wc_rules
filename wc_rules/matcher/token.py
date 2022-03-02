from dataclasses import dataclass,replace
from ..schema.base import BaseClass
from typing import Dict, Tuple, Any

# A token is something you pass TO the ReteNet
@dataclass(eq=True)
class Token:
	classref: type
	action: str
	data: Dict
	channel: int = -1

	def copy(self,channel):
		return replace(self,channel=channel)

def make_node_token(_class,ref,action,channel=-1):
	return Token(classref=_class,data={'ref':ref},action=action,channel=channel)

# def make_node_token(_class,ref,action):
# 	return dict(_class=_class,ref=ref,action=action)

# def make_edge_token(_class1,ref1,attr1,ref2,attr2,action):
# 	return dict(_class=_class1,ref1=ref1,attr1=attr1,ref2=ref2,attr2=attr2,action=action)

# def make_attr_token(_class,ref,attr,value,action):
# 	return dict(_class=_class,ref=ref,attr=attr,value=value,action=action)

# def make_cache_token(variables,values,action):
# 	return dict(variables=variables,values=values,action=action)

