from frozendict import frozendict
from collections import deque,Counter
from ..utils.collections import merge_lists,triple_split, subdict, merge_dicts, no_overlaps

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
	entry, action = channel.data.mapping.transform(elem['entry']), elem['action']
	if action not in ['AddEntry','RemoveEntry']:
		return net
	if action == 'AddEntry':
		entries = [entry]
		channels = [x for x in net.get_channels({'source':channel.source,'type':'merge'}) if x!=channel]	
		while channels:
			channels = deque(sort_channels(channels,entries[0].keys()))
			ch = channels.popleft()
			entries = merge_lists([merge_from(net,e,ch.data.mapping,ch.source) for e in entries])
	if action == 'RemoveEntry':
		entries = net.filter_cache(channel.target,entry)

	node = net.get_node(core=channel.target)
	for e in entries:
		node.state.incoming.append({'entry':e,'action':action})
	return net

def sort_channels(channels,variables):
	# maximize sharing, minimize number of variables that need to be extended to
	def shared(ch):
		return len(set(variables).intersection(ch.data.mapping.targets))
	def total(ch):
		return len(ch.data.mapping.targets)
	return sorted(channels,key = lambda ch: (-shared(ch),total(ch),) )

def merge_from(net,entry,mapping,source):
	# the filter condition on the cache is:
	#   keys shared between entry and mapping.targets must have the same values
	# the reject condition on any candidate for merging:
	#   keys unique to entry and mapping.targets must have unique values
	merges = []
	L, M, R = triple_split(entry.keys(),mapping.targets)
	Ld, Md = [subdict(entry,x) for x in [L,M]]
	for x in net.filter_cache(source,mapping.reverse().transform(Md)):
		Rd = subdict(mapping.transform(x),R)
		if no_overlaps([Ld.values(),Rd.values()]):
			merges.append(merge_dicts([Ld,Md,Rd]))
	return merges

def print_channel(channel,tab=''):
	L = ['Channel:',hash(channel.source)%100, hash(channel.target)%100, channel.data.mapping]
	return tab + ' '.join([str(x) for x in L])



default_functionalization_methods = [method for name,method in globals().items() if name.startswith('function_')]