""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
import wc_rules.graph_utils as g
import wc_rules.utils as utils
import uuid
import random


# Seed for creating ids
# To modify this seed, load base module, then execute base.idgen.seed(<new_seed>)
idgen = random.Random()
idgen.seed(0)

###### Structures ######
class BaseClass(core.Model):
	"""	Base class for bioschema objects.
	Attributes:
	* id (:obj:`str`): unique id that can be used to pick object from a list
	Properties:
	* label (:obj:`str`): name of the leaf class from which object is created
	"""
	id = core.StringAttribute(primary=True,unique=True)
	attribute_properties = dict()

	class GraphMeta(g.GraphMeta):
		outward_edges = tuple()
		semantic = tuple()

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		if 'id' not in kwargs.keys():
			self.id = str(uuid.UUID(int=idgen.getrandbits(128)))

		self.attribute_properties = self.make_attribute_properties_dict()
		self.addable_classes = self.make_addable_class_dict()

	def make_attribute_properties_dict(self):
		attrdict = dict()
		cls = self.__class__

		def populate_attribute(attrname,attr,check = 'related_class'):
			x = {'related':False,'append':False,'related_class':None}
			if check=='related_class' and hasattr(attr,'related_class'):
				x['related'] = True
				x['related_class'] = attr.related_class
				if isinstance(attr,(core.OneToManyAttribute,core.ManyToManyAttribute,)):
					x['append'] = True
			elif check=='primary_class' and hasattr(attr,'primary_class'):
				x['related'] = True
				x['related_class'] = attr.primary_class
				if isinstance(attr,(core.ManyToManyAttribute,core.ManyToOneAttribute,)):
					x['append'] = True
			return x

		for attrname,attr in cls.Meta.attributes.items():
			attrdict[attrname] = dict()
			attrdict[attrname].update(populate_attribute(attrname,attr,'related_class'))
		for attrname,attr in cls.Meta.related_attributes.items():
			if attrname not in attrdict:
				attrdict[attrname] = dict()
			attrdict[attrname].update(populate_attribute(attrname,attr,'primary_class'))

		return attrdict

	def make_addable_class_dict(self):
		d = self.attribute_properties
		clsdict = dict()

		for attrname in d:
			if d[attrname]['related']:
				rel = d[attrname]['related_class']
				if rel not in clsdict:
					clsdict[rel] = {'attrnames':list(),'easy_add':True}
				else:
					clsdict[rel]['easy_add'] = False
				clsdict[rel]['attrnames'].append(attrname)
		return clsdict


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

	def find_attr_by_name(self,attrname):
		try:
			attr = getattr(self,attrname)
		except:
			raise utils.FindError('Could not get attribute {}'.format(attrname))
		return attr

	# not-so-clever methods
	def filter_by_attrname(self,attrname,**kwargs):
		attr = self.find_attr_by_name(attrname)
		return attr.filter(**kwargs)

	def get_by_attrname(self,attrname,**kwargs):
		attr = self.find_attr_by_name(attrname)
		return attr.get(**kwargs)

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

	def set_by_attrname(self,obj,attrname,force=False):
		attr = self.find_attr_by_name(attrname)
		if force or attr is None:
			try:
				setattr(self,attrname,obj)
				str1 = '\'' + attrname + '\''
				if str1 in str(getattr(self,attrname).validate()):
					raise utils.SetError('Data type incompatible with attribute \'{}\'.'.format(attrname))
			except:
				raise utils.SetError('Unable to set value of attribute \'{}\'.'.format(attrname))
		else:
			raise utils.SetError('Attribute \'{}\' already set. Unset or use force=True.'.format(attrname))
		return self

	def unset_by_attrname(self,attrname):
		attr = self.find_attr_by_name(attrname)
		try:
				setattr(self,attrname,None)
		except:
			raise utils.SetError('Unable to unset value of attribute \'{}\'.'.format(attrname))
		return self

	# clever methods
	def ifilter(self,**kwargs):
		ret = []
		for attrname in self.attribute_properties:
			attr = self.find_attr_by_name(attrname)
			if attr is not None:
				if self.attribute_properties[attrname]['related']:
					ret.extend(attr.filter(**kwargs))
		ret2 = []
		for x in ret:
			if x not in ret2:
				ret2.append(x)
		return ret2

	def iget(self,**kwargs):
		ret = self.ifilter(**kwargs)
		if len(ret)>1:
			raise utils.FindError('More than one instance found.')
		elif len(ret)==1:
			ret = ret[0]
		elif len(ret)==0:
			ret = None
		return ret

	def get_compatible_attribute_names(self,obj):
		attrnames = []
		for x in self.addable_classes:
			if isinstance(obj,x):
				for y in self.addable_classes[x]['attrnames']:
					if y not in attrnames:
						attrnames.append(y)
		return attrnames

	def iadd(self,obj,attrname=None,force=False):
		if type(obj) is list:
			for x  in obj:
				self.iadd(x,attrname)
			return self
		if attrname is None:
			compatible_attrnames = self.get_compatible_attribute_names(obj)
			if len(compatible_attrnames) == 0:
				raise utils.AddError('No compatible attribute found.')
			if len(compatible_attrnames) > 1:
				raise utils.AddError('Multiple compatible attributes found. Be more specific.')
			attrname = compatible_attrnames[0]
		if self.attribute_properties[attrname]['append']:
				self.add_by_attrname(obj,attrname)
		else:
				self.set_by_attrname(obj,attrname,force=force)
		return self

	def iremove(self,obj,attrname=None):
		if type(obj) is list:
			for x in obj:
				self.iremove(x,attrname)
			return self
		if attrname is None:
			compatible_attrnames = self.get_compatible_attribute_names(obj)
			attrs_present = []
			for x in compatible_attrnames:
				if self.attribute_properties[x]['append']:
					if obj in getattr(self,x):
						attrs_present.append(x)
				else:
					if getattr(self,x) is obj:
						attrs_present.append(x)
			if len(attrs_present)==0:
				raise utils.RemoveError('Object not found.')
			if len(attrs_present)>1:
				raise utils.RemoveError('Multiple instances found. Be more specific.')
			attrname = attrs_present[0]
		if self.attribute_properties[attrname]['append']:
			self.remove_by_attrname(obj,attrname)
		else:
			self.unset_by_attrname(attrname)
		return self


	def attributes_that_contain(self,obj):
		attrlist = self.get_compatible_attribute_names(obj)
		ret = []
		for attrname in attrlist:
			if self.attribute_properties[attrname]['append']:
				if obj in getattr(self,attrname):
					ret.append(attrname)
			else:
				if obj is getattr(self,attrname):
					ret.append(attrname)
		return ret

	def __contains__(self,obj):
		return len(self.attributes_that_contain(obj))>0


	##### Graph Methods #####
	def get_graph(self,recurse=True,memo=None):
		return g.get_graph(self,recurse=recurse,memo=memo)

	@property
	def graph(self):
		return self.get_graph(recurse=True)

class DictClass(core.Model,dict):pass

def main():
	pass

if __name__ == '__main__':
	main()
