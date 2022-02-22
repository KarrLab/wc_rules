from ..schema.base import BaseClass
from ..schema.chem import Molecule

class InitializeBehaviors:

	def check_exists_node(self,**kwargs):
		return self.get_node(**kwargs) is not None

	def initialize_start(self):
		self.add_node(type='start',core=BaseClass)
		return self

	def initialize_class(self,_class):
		if not self.check_exists_node(core=_class):
			parent = _class.__mro__[1]
			self.initialize_class(parent)
			self.add_node(type='class',core=_class)
			self.add_channel(type='pass',source=parent,target=_class)
		return self

	def initialize_receiver(self,**kwargs):
		node = self.get_node(**kwargs)
		receiver_name = f'receiver_{node.num}'
		self.add_node(type='receiver',core=receiver_name,cachetype='deque')
		self.add_channel(type='pass',source=node.core,target=receiver_name)
		return self

