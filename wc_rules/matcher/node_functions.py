# see tokens.py for the different types of tokens

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
		return self

	def function_node_canonical_label_single_node(self,node,token):
		if token.action =='AddEntry':
			node.state.cache.insert(token.data)
			node.state.outgoing.append(token)
		if token.action == 'RemoveEntry':
			deleted = node.state.cache.delete(token.data)
			node.state.outgoing.append(token)
		return self