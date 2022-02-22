# see tokens.py for the different types of tokens

class FunctionalizeNodes:

	def function_node_start(self,node,token):
		self.function_node_class(node,token)
		return self
		
	def function_node_class(self,node,token):
		if issubclass(token['_class'],node.core):
			node.state.outgoing.append(token)
		return self

	def function_node_receiver(self,node,token):
		node.state.cache.append(token)
		return self
