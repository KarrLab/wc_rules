from ...schema.base import BaseClass
from ...utils.random import generate_id
# nodes must be a dict with keys
# 'type','core',
# 'state' gets automatically initialized
# other keys get pushed into **data

def initialize_start(net):
	net.add_node(type='start',core=BaseClass)
	return net

def initialize_class(net,_class):
	if net.get_node(core=_class) is None:
		net.add_node(type='class',core=_class)
		parent = _class.__mro__[1]
		net.initialize_class(parent)
		net.add_channel(type='pass',source=parent,target=_class)
	return net

def initialize_collector(net,source,label):
	idx = f'collector_{label}'
	net.add_node(type='collector',core=idx)
	net.add_channel(type='pass',source=source,target=idx)
	return net


