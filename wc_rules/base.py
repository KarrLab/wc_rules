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
	
	
	_attribute_properties = dict()
	_attributes_populated = False
	_where_to_add = dict()
	
	def __init__(self,**kwargs):
		super(BaseClass,self).__init__(**kwargs)
		if not self.__class__._attributes_populated:
			self.__class__.populate_attribute_properties()
			self.__class__._attributes_populated = True
		return
	
	@classmethod
	def populate_attribute_properties(cls):
		if len(cls._attribute_properties) == 0:
			to_one_types = (core.OneToOneAttribute,core.ManyToOneAttribute,)
			to_many_types = (core.OneToManyAttribute,core.ManyToManyAttribute,)
			one_to_types = (core.OneToOneAttribute,core.OneToManyAttribute,)
			many_to_types = (core.ManyToManyAttribute,core.ManyToOneAttribute,)
					
			for attrname,attr in list(cls.Meta.attributes.items()):
				cls._attribute_properties[attrname] = dict()
				if hasattr(attr,'related_class'):
					cls._attribute_properties[attrname]['related'] = True
					cls._attribute_properties[attrname]['related_class'] = attr.related_class
					if isinstance(attr,to_one_types):
						cls._attribute_properties[attrname]['append'] = False
					if isinstance(attr,to_many_types):
						cls._attribute_properties[attrname]['append'] = True
				else:
					cls._attribute_properties[attrname]['related'] = False
					cls._attribute_properties[attrname]['append'] = False
			for attrname,attr in list(cls.Meta.related_attributes.items()):
				cls._attribute_properties[attrname] = dict()
				if hasattr(attr,'primary_class'):
					cls._attribute_properties[attrname]['related'] = True
					cls._attribute_properties[attrname]['related_class'] = attr.primary_class
					if isinstance(attr,one_to_types):
						cls._attribute_properties[attrname]['append'] = False
					if isinstance(attr,many_to_types):
						cls._attribute_properties[attrname]['append'] = True
				else:
					cls._attribute_properties[attrname]['related'] = False
					cls._attribute_properties[attrname]['append'] = False
		for attrname in cls._attribute_properties:
			if cls._attribute_properties[attrname]['related']:
				related_class = cls._attribute_properties[attrname]['related_class']
				if related_class not in cls._where_to_add:
					cls._where_to_add[related_class] = []
				cls._where_to_add[related_class].append(attrname)	
		return

	def find_attr_by_name(self,attrname):
		try:
			attr = getattr(self,attrname)
		except:
			raise utils.FindError('Could not get attribute {}'.format(attrname))
		return attr
		
	def add_by_attrname(self,obj,attrname):
		attr = self.find_attr_by_name(attrname)
		try:
			attr.append(obj)
		except:
			raise utils.AddError('Could not add object to attribute \'{}\'.'.format(attrname))
		return self
		
	def remove_by_attrname(self,obj,attrname,force=True):
		attr = self.find_attr_by_name(attrname)
		if obj not in attr:
			raise utils.RemoveError('Object not found in attribute \'{}\'.'.format(attrname))
		try:
			attr.remove(obj)
		except:
			raise utils.RemoveError('Could not remove object from attribute \'{}\'.'.format(attrname))
		return self
		
	def set_by_attrname(self,obj,attrname,force=True):
		attr = self.find_attr_by_name(attrname)
		if force or attr is None:
			try:
				setattr(self,attrname,obj)
			except:
				raise utils.SetError('Unable to set value of attribute \'{}\'.'.format(attrname))
		else:
			raise utils.SetError('Attribute {} already set. Unset or use force=True.'.format(attrname))
		return self
		
	def unset_by_attrname(self,attrname):
		attr = self.find_attr_by_name(attrname)
		try:
			setattr(self,attrname,None)
		except:
			raise utils.SetError('Unable to unset value of attribute \'{}\'.'.format(attrname))
		return self

	##### Graph Methods #####
	def get_graph(self,recurse=True,memo=None):
		return g.get_graph(self,recurse=recurse,memo=memo)
		
	@property
	def graph(self):
		return self.get_graph(recurse=True)

class Entity(BaseClass):pass
class Operation(BaseClass):
	targets = core.ManyToManyAttribute(Entity,related_name='operations')
	

def main():
	pass
		
if __name__ == '__main__': 
	main()

