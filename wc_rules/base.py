""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
import wc_rules.graph_utils as g
import wc_rules.utils as utils

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
	_can_append = None
	@property
	def related_types(self):
		''' A dictionary {attrname:class} of related classes '''
		if self._related_types is None:
			type_dict = dict()
			append_dict = dict()
			for attrname,attr in list(self.__class__.Meta.attributes.items()):
				if hasattr(attr,'related_class'):
					type_dict[attrname] = attr.related_class
					to_one_types = (core.OneToOneAttribute,core.ManyToOneAttribute,)
					to_many_types = (core.OneToManyAttribute,core.ManyToManyAttribute,)
					if isinstance(attr,to_one_types):
						append_dict[attrname] = False
					if isinstance(attr,to_many_types):
						append_dict[attrname] = True
			for attrname,attr in list(self.__class__.Meta.related_attributes.items()):
				if hasattr(attr,'primary_class'):
					type_dict[attrname] = attr.primary_class
					one_to_types = (core.OneToOneAttribute,core.OneToManyAttribute,)
					many_to_types = (core.ManyToManyAttribute,core.ManyToOneAttribute,)
					if isinstance(attr,one_to_types):
						append_dict[attrname] = False
					if isinstance(attr,many_to_types):
						append_dict[attrname] = True		
			self._related_types = type_dict
			self._can_append = append_dict
		return self._related_types
	@property
	def can_append(self):
		''' A dictionary {attrname:bool} to indicate whether to append method can be used '''
		if self._can_append is None:
			# This is simply to trigger building the dictionary
			x = self.related_types		
		return self._can_append
		
	def get_compatible_attributes(self,obj):
		possible_attrs = []
		for attrname,attrtype in self.related_types.items():
			if isinstance(obj,attrtype):
				possible_attrs.append(attrname)
		return possible_attrs
				
	
	def add_by_attrname(self,obj,attrname,force=False):
		# first check if attribute exists
		# then check if object to be added is a list
		#        if attribute itself is not a list, raise error, else recurse into obj list
		# check if attr is compatible with obj, if not raise error
		# check if attr is a list, if so, attr.append(obj)
		# if not, check if it already has been set, then raise error unless force=True
		# set attr=obj
		if attrname not in self.related_types.keys():
			raise utils.AddError('Attribute \'{}\' not found.'.format(attrname))
		if isinstance(obj,list):
			if not self.can_append[attrname]:
				raise utils.AddError('Attribute \'{}\' not a list.'.format(attrname))
			for x in obj:
				self.add_by_attrname(x,attrname=attrname)
			return self
		if attrname not in self.get_compatible_attributes(obj):
			raise utils.AddError('Attribute \'{}\' not compatible.'.format(attrname))
		if self.can_append[attrname]:
			getattr(self,attrname).append(obj)
		else:
			if (getattr(self,attrname) is not None) and (not force):
				raise utils.AddError('Attribute \'{}\' already set. Either unset first or use force=True.'.format(attrname))
			setattr(self,attrname,obj)
		return self

	
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

