from frozendict import frozendict
from collections import deque,Counter
#from ..utils.collections import merge_lists,triple_split, subdict, merge_dicts, no_overlaps, tuplify_dict
from ..utils.collections import merge_dicts_strictly, is_one_to_one

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
	
	if elem['action'] == 'AddEntry':
		assert net.filter_cache(clabel,entry) == []
		net.insert_into_cache(clabel,entry)
	if elem['action'] == 'RemoveEntry':
		assert net.filter_cache(clabel,entry) != []
		net.remove_from_cache(clabel,entry)
	node.state.outgoing.append({'entry':entry,'action':action})
	return net

def function_node_pattern(net,node,elem):
	if node.data.get('alias',False):
		node.state.outgoing.append(elem)
	else:
		assert False, "Not Yet!"
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

def function_channel_merge(net,channel,elem):
	action = elem['action']

	if action in ['AddEntry', 'RemoveEntry']:
		entry = channel.data.mapping.transform(elem['entry'])
		if action == 'AddEntry':
			merge_channels = net.get_channels({'target':channel.target,'type':'merge'}) 
			assert len(merge_channels) == 2
			ch = [x for x in merge_channels if x.num != channel.num][0]
			fMapping, rMapping, entries = ch.data.mapping, ch.data.mapping.reverse(), []
			for x in net.filter_cache(ch.source, rMapping.transform(entry)):
				d = merge_dicts_strictly([entry,fMapping.transform(x)])
				if is_one_to_one(d):
					entries.append(d)
		elif action == 'RemoveEntry':
			entries = net.filter_cache(channel.target,entry)
		node = net.get_node(core=channel.target)	
		for e in entries:
			node.state.incoming.append({'entry':e,'action':action})
	return net

def function_channel_alias(net,channel,elem):
	outd = {k:v for k,v in elem.items() if k!='entry'}
	outd['entry'] = channel.data.mapping.transform(elem['entry'])
	node = net.get_node(core=channel.target)
	node.state.incoming.append(outd)
	return net

default_functionalization_methods = [method for name,method in globals().items() if name.startswith('function_')]