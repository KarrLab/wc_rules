from ..schema.actions import NodeAction, EdgeAction, AddNode, RemoveNode, AddEdge, RemoveEdge, SetAttr
from functools import wraps
# interface
# def function_{node/channel}_{type}(net,node/channel,elem):
#	----
#	return net


def function_node_start(net,node,elem):
	node.state.outgoing.append(elem)
	return net

def function_node_class(net,node,elem):
	return net

def function_node_collector(net,node,elem):
	return net

def function_channel_pass(net,channel,elem):
	return net

default_functionalization_methods = [method for name,method in globals().items() if name.startswith('function_')]