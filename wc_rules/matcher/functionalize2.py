from abc import ABC, abstractmethod
class SuperSet:

	def __contains__(self,x):
		return True


class Behavior(ABC):
	callsign = ''
	actions = SuperSet()

	# an INSTANCE of Behavior works like a method
	# can be bound to ReteNet using net.add_behavior()

	@classmethod
	def subclass_iter(cls):
		subs = cls.__subclasses__()
		for sub in subs:
			yield sub
			for x in sub.subclass_iter():
				yield x

	def do(self,**kwargs):
		return [],[]		
	
	@abstractmethod
	def __call__(self,**kwargs):
		return net

	def entry_check(self,node,elem):
		return elem.get('action','') in self.actions
	
class NodeBehavior(Behavior):

	def __call__(self,net,node,elem):
		if self.entry_check(node,elem):
			if isinstance(self.actions,SuperSet):
				fn = getattr(self,'do')
			else:	
				fn = getattr(self,f"do_{elem['action']}")
			incoming,outgoing = fn(net,node,elem)
			node.state.incoming.extend(incoming)
			node.state.outgoing.extend(outgoing)
		return net

class StartNode(NodeBehavior):
	callsign = 'start'

	def do(self,net,node,elem):
		return [], [elem]
	
class ClassNode(NodeBehavior):
	callsign = 'class'

	def entry_check(self,node,elem):
		return issubclass(elem['_class'],node.core)

	def do(self,net,node,elem):
		return [], [elem]

class CanonicalLabelNode(NodeBehavior):
	callsign = 'canonical_label'
	actions = set(['AddEntry','RemoveEntry'])

	def do_AddEntry(self,net,node,elem):
		clabel,entry = node.core, elem['entry']
		# assert net.filter_cache(clabel,entry) == []
		net.insert_into_cache(clabel,entry)
		return [],[elem]

	def do_RemoveEntry(self,net,node,elem):
		clabel,entry = node.core, elem['entry']
		# assert net.filter_cache(clabel,entry) != []
		net.remove_from_cache(clabel,entry)
		return [], [elem]
				

