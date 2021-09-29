from frozendict import frozendict


def function_node_start(net,node,elem):
	node.state.outgoing.append(elem)
	return net

def function_node_class(net,node,elem):
	if issubclass(elem['_class'],node.core):
		node.state.outgoing.append(elem)
	return net

def function_node_collector(net,node,elem):
	node.state.cache.append(elem)
	return net

def function_node_canonical_label(net,node,elem):
	clabel = node.core
	entry, action = [elem[x] for x in ['entry','action']]
	if len(clabel.names)<=2:
		# its a single node graph
		if elem['action'] == 'AddEntry':
			assert net.filter_cache(clabel,entry) == []
			net.insert_into_cache(clabel,entry)
		if elem['action'] == 'RemoveEntry':
			assert net.filter_cache(clabel,entry) != []
			net.remove_from_cache(clabel,entry)
		node.state.outgoing.append({'entry':entry,'action':action})
	return net

def function_channel_pass(net,channel,elem):
	target = net.get_node(core=channel.target)
	target.state.incoming.append(elem)
	return net

def function_channel_transform_node_token(net,channel,elem):
	if elem['action'] in ['AddNode','RemoveNode']:
		action = {'AddNode':'AddEntry','RemoveNode':'RemoveEntry'}[elem['action']]		
		entry = channel.data.mapping.transform(elem)
		d = {'entry':entry,'action':action}
		node = net.get_node(core=channel.target)
		node.state.incoming.append(d)
	return net

def function_channel_transform_edge_token(net,channel,elem):
	if elem['action'] in ['AddEdge','RemoveEdge']:
		action = {'AddEdge':'AddEntry','RemoveEdge':'RemoveEntry'}[elem['action']]
		entry = channel.data.mapping.transform(elem)
		d = {'entry':entry,'action':action}
		node = net.get_node(core=channel.target)
		node.state.incoming.append(d)
	return net



default_functionalization_methods = [method for name,method in globals().items() if name.startswith('function_')]