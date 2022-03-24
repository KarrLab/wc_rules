from operator import attrgetter

def list_to_str(L,sep=',',lparen='(',rparen=')'):
	return f'{lparen}{sep.join(L)}{rparen}'

def arrow_str(lhs,rhs,arrow='=>'):
	return f'{lhs} {arrow} {rhs}'

def zip_dict(d):
	return zip(*d.items())

def arrow_str_lists(lists,arrow='=>'):
	return arrow_str(*map(list_to_str,lists),arrow=arrow)

def arrow_str_dict(d,arrow='=>'):
	return arrow_str_lists([d.keys(),d.values()])

class PrintMethods:

	def pprint(self,nodes=None,channels=None):
		s = []
		if nodes is None:
			nodes = self.get_nodes()
		if channels is None:
			channels = self.get_channels()
		if nodes:
			s.append('Nodes')
		for node in nodes:
			description = getattr(self,f'descr_node_{node.type}',self.descr_node_default)(node.core)
			s.append(f'{node.num} {node.type} {description}')
		if nodes and channels:
			s.append('')
		if channels:
			s.append('Channels')
		for channel in channels:
			description = getattr(self,f'descr_channel_{channel.type}',self.descr_channel_default)(channel)
			source,target = [self.get_node(core=getattr(channel,x)).num for x in ['source','target']]
			s.append(f'{channel.num} {channel.type} {source}:{target} {description}')
		return '\n'.join(s)

	def pprint_receivers(self):
		s = []
		s.append('\nReceivers')
		for node in sorted(self.get_nodes(type='receiver'),key=attrgetter('core')):
			s.append(node.core)
			for elem in node.state.cache:
				s.append(f' {str(elem)}')
			s.append(f' len: {len(node.state.cache)}')
		return '\n'.join(s)


	def descr_channel_default(self,channel):
		return ''

	def descr_channel_transform(self,channel):
		return arrow_str_dict(channel.data.transformer.datamap)
		
	def descr_node_default(self,core_obj):
		if isinstance(core_obj,str):
			return core_obj
		if hasattr(core_obj,'__name__'):
			return core_obj.__name__
		return str(core_obj)

	def descr_node_canonical_label(self,core_obj):
		classnames = [x.__name__ for x in core_obj.classes]
		return arrow_str_lists([core_obj.names,classnames])
		
