from dataclasses import dataclass,replace
from ..schema.base import BaseClass
from typing import Dict, Tuple, Any

# A token is something you pass TO the ReteNet
@dataclass(eq=True,frozen=True)
class BasicToken:
	classref: type
	action: str
	data: Dict

@dataclass(eq=True)
class CacheToken:
	action: str
	data: Dict
	channel: int=-1

@dataclass(eq=True)
class VarToken:
	variable: str

class TokenTransformer:
	def __init__(self,datamap,actionmap):
		self.datamap = datamap
		self.actionmap = actionmap

	def transform(self,token,channel=-1):
		if self.datamap is not None:
			data = {self.datamap[k]:v for k,v in token.data.items()}
		else:
			data = token.data
		action = self.actionmap[token.action]
		return CacheToken(data=data,action=action,channel=channel)

def make_node_token(_class,ref,action):
	return BasicToken(classref=_class,data={'ref':ref},action=action)

def make_edge_token(_class1,ref1,attr1,_class2,ref2,attr2,action):
	data = {'ref1':ref1,'attr1':attr1,'ref2':ref2,'attr2':attr2}
	return BasicToken(classref=_class1,data=data,action=action)

def make_attr_token(_class,ref,attr,action):
	return BasicToken(classref=_class,data={'ref':ref,'attr':attr},action=action)

# def make_node_token(_class,ref,action):
# 	return dict(_class=_class,ref=ref,action=action)

# def make_edge_token(_class1,ref1,attr1,ref2,attr2,action):
# 	return dict(_class=_class1,ref1=ref1,attr1=attr1,ref2=ref2,attr2=attr2,action=action)

# def make_attr_token(_class,ref,attr,value,action):
# 	return dict(_class=_class,ref=ref,attr=attr,value=value,action=action)

# def make_cache_token(variables,values,action):
# 	return dict(variables=variables,values=values,action=action)

