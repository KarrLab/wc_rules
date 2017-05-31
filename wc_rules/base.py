""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
import wc_rules.graph_utils as g

###### Structures ######
class BaseClass(core.Model):
	"""	Base class for bioschema objects.
	Attributes:
	* id (:obj:`str`): unique id that can be used to pick object from a list
	Properties:
	* label (:obj:`str`): name of the leaf class from which object is created
	"""
	id = core.StringAttribute(primary=True,unique=True)
	class GraphMeta(g.GraphMeta): 
		outward_edges = tuple()
		semantic = tuple()
	def set_id(self,id):
		""" Sets id attribute.
		Args:
			id (:obj:`str`) 
		Returns:
			self
		"""
		self.id = id
		return self
	
	@property
	def label(self): 
		""" Name of the leaf class from which object is created.
		"""
		return self.__class__.__name__
	
	_related_types = None
	
	@property
	def related_types(self):
		''' A dictionary {attrname:class} of related classes '''
		if self._related_types is None:
			type_dict = dict()
			for attrname,attr in list(self.__class__.Meta.attributes.items()):
				if hasattr(attr,'related_class'):
					type_dict[attrname] = attr.related_class
			for attrname,attr in list(self.__class__.Meta.related_attributes.items()):
				if hasattr(attr,'primary_class'):
					type_dict[attrname] = attr.primary_class
			self._related_types = type_dict
		return self._related_types
	
	##### Graph Methods #####
	def get_graph(self,recurse=True,memo=None):
		return g.get_graph(self,recurse=recurse,memo=memo)
		
	@property
	def graph(self):
		return self.get_graph(recurse=True)


def main():
	pass
		
if __name__ == '__main__': 
	main()

