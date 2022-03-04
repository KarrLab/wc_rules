# see tokens.py for the different types of tokens
from ..utils.collections import subdict
from .token import CacheToken

class NodeFunctions:

	def function_node_start(self,node,token):
		self.function_node_class(node,token)
		return self
		
	def function_node_class(self,node,token):
		if issubclass(token.classref,node.core):
			node.state.outgoing.append(token)
		return self

	def function_node_receiver(self,node,token):
		node.state.cache.append(token)
		return self

	def function_node_canonical_label(self,node,token):
		if len(node.core.names)==1:
			self.function_node_canonical_label_single_node(node,token)
		if len(node.core.names)==2:
			self.function_node_canonical_label_single_edge(node,token)
		return self

	def function_node_canonical_label_single_node(self,node,token):
		self.function_node_cache(node,token)
		return self

	def function_node_canonical_label_single_edge(self,node,token):
		b,attr1,attr2 = subdict(token.data,['b','attr1','attr2']).values()
		L = node.core
		if not (isinstance(b,L.classes[1]) and L.edges[0].attrs()==(attr1,attr2)):
			return self
		newtoken = CacheToken(data=subdict(token.data,['a','b']),action=token.action)
		self.function_node_cache(node,newtoken)
		return self

	def function_node_cache(self,node,token):
		if token.action =='AddEntry':
			node.state.cache.insert(token.data)
			node.state.outgoing.append(token)
		if token.action == 'RemoveEntry':
			deleted = node.state.cache.delete(token.data)
			node.state.outgoing.append(token)
		return self