from frozendict import frozendict
from collections import deque, Counter, ChainMap
#from ..utils.collections import merge_lists,triple_split, subdict, merge_dicts, no_overlaps, tuplify_dict
from ..utils.collections import merge_dicts_strictly, is_one_to_one
from copy import deepcopy
from attrdict import AttrDict

def function_node_start(net,node,elem):
	node.state.outgoing.append(elem)
	return net

def function_node_end(net,node,elem):
	node.state.cache.append(elem)
	return

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
	
	if action == 'AddEntry':
		assert net.filter_cache(clabel,entry) == []
		net.insert_into_cache(clabel,entry)
	if action == 'RemoveEntry':
		assert net.filter_cache(clabel,entry) != []
		net.remove_from_cache(clabel,entry)
	node.state.outgoing.append({'entry':entry,'action':action})
	return net

def run_match_through_constraints(match,helpers,parameters,constraints):
	extended_match = ChainMap(match,helpers,parameters)
	terminate_early = False
	for c in constraints:
		value = c.exec(extended_match)
		if c.deps.declared_variable is not None:
			extended_match[c.deps.declared_variable] = value
		elif not value:
			return None
	return match
		
def function_node_pattern(net,node,elem):
	if node.data.get('alias',False):
		node.state.outgoing.append(elem)
		return net
	entry, action= [elem[x] for x in ['entry','action']]
	outgoing_entries = []
	if action == 'AddEntry':
		match = {k:v for k,v in entry.items()}
		match = run_match_through_constraints(match, node.data.helpers, node.data.parameters, node.data.constraints)
		if match is not None:
			net.insert_into_cache(node.core,match)
			node.state.outgoing.append({'entry':match,'action':action})
	if action == 'RemoveEntry':
		elems = net.filter_cache(node.core,entry)
		net.remove_from_cache(node.core,entry)
		for e in elems:
			node.state.outgoing.append({'entry':e,'action':action})
		
	if action == 'UpdateEntry':
		# update entry is resolved to AddEntry or RemoveEntry and inserted back into incoming queue
		# ReteNet.sync(node) runs until incoming is empty
		
		match = {k:v for k,v in entry.items()}
		existing_elems = net.filter_cache(node.core,entry)
		match = run_match_through_constraints(match,node.data.helpers,node.data.parameters,node.data.constraints)
		if match is None:
			if len(existing_elems) > 0:
				for e in existing_elems:
					node.state.incoming.append({'entry':e,'action':'RemoveEntry'})
		elif match is not None:
			if len(existing_elems) == 0:
				node.state.incoming.append({'entry':match,'action':'AddEntry'})

	return net

def function_node_rule(net,node,elem):
	if elem['action']=='UpdateRule':
		old = node.state.cache
		node.state.cache = new = node.data.propensity.exec(node.data.reactants,node.data.helpers,node.data.parameters)
		if old != new:
			node.state.outgoing.append({'source':node.core,'propensity':node.state.cache,'action':'NotifyUpdatedRule'})
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

def function_channel_parent(net,channel,elem):
	action = elem['action']
	if action in ['AddEntry', 'RemoveEntry']:
		node = net.get_node(core=channel.target)
		entry = channel.data.mapping.transform(elem['entry'])
		node.state.incoming.append({'entry':entry,'action':action})
	return net

def function_channel_update_pattern(net,channel,elem):
	action = elem['action']
	
	if action in  ['AddEdge','RemoveEdge','SetAttr','AddEntry','RemoveEntry']:
		# it asks for parent of the target
		# then filters the parent cache to get candidate entries for target
		# then asks target to do 'UpdateEntry' on all candidates
		if action in ['AddEdge','RemoveEdge']:
			attr = elem['attr1']
		elif action == 'SetAttr':
			attr = elem['attr']
		else:
			attr = None
			
		node = net.get_node(core=channel.target)
		entry = channel.data.mapping.transform(elem)
		parent_channel = net.get_channel(target=channel.target,type='parent')
		parent = parent_channel.source
		parent_mapping = parent_channel.data.mapping
		filterelem = parent_mapping.reverse().transform(entry)
		elems = [parent_mapping.transform(x) for x in net.filter_cache(parent,filterelem)]
		for e in elems:
			node.state.incoming.append({'entry':e,'action':'UpdateEntry','attr':attr})		
	return net

def function_channel_update_rule(net,channel,elem):
	# TODO: A generic update_rule that accounts for using helper patterns
	if elem['action'] in ['AddEntry','RemoveEntry']:
		node = net.get_node(core=channel.target)
		node.state.incoming.append({'action':'UpdateRule','source':channel.source})
	return net

def function_sample_rule(net,rname):
	rule = net.get_node(core=rname,type='rule')
	sample = dict()
	for var, pstate in rule.data.reactants.items():
		sample[var] = AttrDict(pstate.sample_cache())
	return sample
	

default_functionalization_methods = [method for name,method in globals().items() if name.startswith('function_')]