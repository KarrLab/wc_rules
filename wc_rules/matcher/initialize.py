from ..schema.base import BaseClass
from ..utils.random import generate_id
from ..utils.collections import Mapping
from collections import deque
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
	net.get_node(type='collector',core=idx).state.cache = deque()
	net.add_channel(type='pass',source=source,target=idx)
	return net

def initialize_canonical_label(net,clabel,symmetry_group):
	if len(clabel.names)<=2 and net.get_node(core=clabel) is None:
		# it is a singleton graph
		net.initialize_class(clabel.classes[0])
		net.add_node(type='canonical_label',core=clabel,symmetry_group=symmetry_group)
		net.initialize_cache(clabel,clabel.names)
		chtype = {1:'node',2:'edge'}[len(clabel.names)]
		mapping = {1:Mapping(['idx'],['a']),2:Mapping(['idx1','idx2'],['a','b'])}[len(clabel.names)]
		net.add_channel(type=f'transform_{chtype}_token',source=clabel.classes[0],target=clabel,mapping=mapping)
	return net


default_initialization_methods = [method for name,method in globals().items() if name.startswith('initialize_')]
