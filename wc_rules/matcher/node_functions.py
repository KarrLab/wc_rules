# see tokens.py for the different types of tokens
from ..utils.collections import subdict
from .token import CacheToken, VarToken

def no_common_values(d1,d2):
	return len(set(d1.values()) & set(d2.values())) == 0

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

	def function_node_end(self,node,token):
		assert isinstance(token,VarToken)
		node.state.cache.add(token.variable)
		return self

	def function_node_canonical_label(self,node,token):
		if len(node.core.names)==1:
			self.function_node_canonical_label_single_node(node,token)
		elif len(node.core.names)==2:
			self.function_node_canonical_label_single_edge(node,token)
		else:
			self.function_node_canonical_label_general_case(node,token)
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

	def function_node_canonical_label_general_case(self,node,token):
		entries = []
		if token.action=='AddPartialEntry':
			channels,caches,keysep = [node.data[x] for x in ['channels','caches','keysep']]
			chA = channels[token.channel]
			chB = {'lhs':'rhs','rhs':'lhs'}[chA]
			query,constant = [subdict(token.data,keysep[x]) for x in ['common',chA]]
			candidates = caches[chB].filter(query)
			entries = [{**constant,**cand} for cand in candidates if no_common_values(constant,cand)]	
		if token.action=='RemovePartialEntry':
			entries = node.state.cache.filter(token.data)
		action = token.action.replace('Partial','')
		for entry in entries:
			newtoken = CacheToken(data=entry,action=action)
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

	def function_node_alias(self,node,token):
		if token.action == 'AddEntry':
			node.state.outgoing.append(token)
		if token.action == 'RemoveEntry':
			node.state.outgoing.append(token)
		return self

	def function_node_constraints(self,node,token):
		executable_manager = node.data.executables
		caches = node.data.caches
		if token.action == 'AddEntry':
			match = executable_manager.exec(token.data,caches)
			if match is not None:
				newtoken = CacheToken(data=match,action='AddEntry')
				self.function_node_cache(node,newtoken)
		elif token.action == 'RemoveEntry':
			self.function_node_cache(node,token)
		elif token.action == 'VerifyEntry':
			for elem in caches.parent.filter(token.data):
				current_matching_elem = node.state.cache.filter_one(elem)
				if current_matching_elem is not None:
					deltoken = CacheToken(data=current_matching_elem,action='RemoveEntry')
					self.function_node_constraints(node,deltoken)
				instoken = CacheToken(data=elem,action='AddEntry')
				self.function_node_constraints(node,instoken)
		else:
			assert False, 'Not supported yet'
		return self

	def function_node_pattern(self,node,token):
		if node.data.subtype == 'alias':
			self.function_node_alias(node,token)
		else:
			self.function_node_constraints(node,token)
		return self

	def function_node_variable(self,node,token):
		if node.data.subtype == 'recompute':
			params = {k:self.get_node(core=c).state.cache.value for k,c in node.data.parameters.items()}
			value = node.data.executable.exec(params,node.data.caches)
			if value != node.state.cache.value:
				node.state.cache.update(value)
				token = VarToken(variable=node.core)
				node.state.outgoing.append(token)
		else:
			assert False, "Not supported yet!"
		return self