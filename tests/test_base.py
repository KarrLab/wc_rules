from wc_rules import base,chem,utils
import wc_rules.graph_utils as g
from obj_model import core
import unittest

class Person(base.BaseClass):
	name = core.StringAttribute()
	parents = core.ManyToManyAttribute('Person',max_related_rev=2,related_name='children')
	pets = core.OneToManyAttribute('Pet',related_name='owner')
	class GraphMeta(g.GraphMeta):
		outward_edges=('children','pets')
		semantic = ('name',)
		
class Pet(base.BaseClass):
		name = core.StringAttribute()

class TestBase(unittest.TestCase):
	def setUp(self):
		base.idgen.seed(0)
		self.Sherlock = Person(name='Sherlock')
		self.John = Person(name='John')
		self.Mary = Person(name='Mary')
		
		self.Kid001 = Person(name='Kid001')
		self.Kid002 = Person(name='Kid002')
		self.Dog001 = Pet(name='Dog001')
	
	@staticmethod
	def list_names(xlist):
		return list(map((lambda x:x.name),xlist))
		
	def test_ids(self):
		all_things = [self.Sherlock, self.John, self.Mary, self.Kid001, self.Kid002, self.Dog001]
		id_arr = [x.id for x in all_things]
		check_str = [
		'e3e70682-c209-4cac-629f-6fbed82c07cd',
		'f728b4fa-4248-5e3a-0a5d-2f346baa9455',
		'eb1167b3-67a9-c378-7c65-c1e582e2e662',
		'f7c1bd87-4da5-e709-d471-3d60c8a70639',
		'e443df78-9558-867f-5ba9-1faf7a024204',
		'23a7711a-8133-2876-37eb-dcd9e87a1613',
		]
		# works only when base.idgen.seed(0) in setUp()
		self.assertEqual(id_arr,check_str)
	
	def test_attribute_properties(self):
		attrprops = self.John.attribute_properties
		keylist = 'id name parents pets children'.split()
		self.assertEqual(list(attrprops.keys()),keylist)
		check_dict = {
			'id':{'related': False, 'append': False},
			'name': {'related': False, 'append': False},
			'parents': {'related': True, 'append': True},
			'pets' : {'related': True, 'append': True},
			'children': {'related': True, 'append': True},
			}
		for x in check_dict:
			for y in ['related','append']:
				self.assertEqual(attrprops[x][y],check_dict[x][y])
				
		self.assertEqual(attrprops['id']['related_class'],None)
		self.assertEqual(attrprops['name']['related_class'],None)
		self.assertEqual(attrprops['parents']['related_class'],type(self.John))
		self.assertEqual(attrprops['pets']['related_class'],type(self.Dog001))
		self.assertEqual(attrprops['children']['related_class'],type(self.Kid001))
		
	def test_addable_classes(self):
		addable_classes = self.John.addable_classes
		cls1 = type(self.John)
		cls2 = type(self.Dog001)
		
		self.assertEqual(addable_classes[cls1]['attrnames'],['parents','children'])
		self.assertEqual(addable_classes[cls2]['attrnames'],['pets'])
		
		self.assertFalse(addable_classes[cls1]['easy_add'])
		self.assertTrue(addable_classes[cls2]['easy_add'])
		
	def test_basic_methods(self):
		Kids = [self.Kid001,self.Kid002]
		Parents = [self.John, self.Mary]
		
		with self.assertRaises(utils.FindError): self.John.find_attr_by_name('car')
		
		for x in Kids:
			for y in Parents:
				x.add_by_attrname(y,'parents')
			
		self.assertEqual(self.list_names(self.Kid001.parents),'John Mary'.split())
		self.assertEqual(self.list_names(self.John.children),'Kid001 Kid002'.split())		
		
		# this should raise an error in obj_model
		#with self.assertRaises(utils.AddError): 
		#	self.Kid001.add_by_attrname(self.Sherlock,'parents')
		
		for y in Kids:
			for x in Parents:
				y.remove_by_attrname(x,'parents')
		
		self.assertEqual(self.list_names(self.Kid001.parents),[])
		self.assertEqual(self.list_names(self.John.children),[])
		
		with self.assertRaises(utils.RemoveError):
			self.Kid001.remove_by_attrname(self.Sherlock,'parents')
		
		self.Dog001.set_by_attrname(self.Sherlock,'owner')
		self.assertEqual(self.Dog001.owner.name,'Sherlock')
		self.assertEqual(self.list_names(self.Sherlock.pets),['Dog001'])
		
		with self.assertRaises(utils.SetError):
			self.John.set_by_attrname(self.Dog001,'children')
			
		with self.assertRaises(utils.SetError):
			self.Sherlock.unset_by_attrname('pets')
		self.Dog001.unset_by_attrname('owner')
		self.assertEqual(self.Sherlock.pets,[])
		self.assertEqual(self.Dog001.owner,None)
		
		self.Kid001.iadd([self.John,self.Mary],'parents')
		x = self.list_names(self.Kid001.filter_by_attrname('parents',label='Person'))
		self.assertEqual(x, 'John Mary'.split())
		x = self.list_names(self.Kid001.filter_by_attrname('parents',label='Persona'))
		self.assertEqual(x, [])
		x = self.Kid001.get_by_attrname('parents',name='John')
		self.assertEqual(x.name, 'John')
		x = self.Kid001.get_by_attrname('parents',name='Johny')
		self.assertEqual(x, None)
		with self.assertRaises(ValueError):
			self.Kid001.get_by_attrname('parents')
		
		self.Kid001.iremove([self.John,self.Mary])
		
		
		
	def test_intelligent_methods(self):
		attrlist = self.John.get_compatible_attribute_names(self.Sherlock)
		self.assertEqual(attrlist,'parents children'.split())
		
		with self.assertRaises(utils.AddError):
			self.John.iadd(object())
		with self.assertRaises(utils.AddError):
			self.John.iadd(self.Mary)
		self.Kid001.iadd([self.John,self.Mary],'parents')
		self.assertEqual(self.list_names(self.Kid001.parents),'John Mary'.split())
		self.Dog001.iadd(self.Sherlock)
		self.assertEqual(self.Dog001.owner.name,'Sherlock')
		
		with self.assertRaises(utils.RemoveError):
			self.Kid001.iremove(self.Sherlock)
			
		self.Kid001.iremove([self.John,self.Mary])
		self.assertEqual(self.Kid001.parents,[])
		self.Dog001.iremove(self.Sherlock)
		self.assertEqual(self.Dog001.owner,None)
			
		self.John.iadd(self.Sherlock,'parents')
		self.John.iadd(self.Sherlock,'children')
		self.assertTrue(self.Sherlock in self.John)
		self.assertEqual(self.John.attributes_that_contain(self.Sherlock),'parents children'.split())
		
		with self.assertRaises(utils.RemoveError):
			self.John.iremove(self.Sherlock)
			
		self.John.iremove(self.Sherlock,'parents')
		self.John.iremove(self.Sherlock,'children')
		self.assertTrue(self.Sherlock not in self.John)
		
		self.Kid001.iadd([self.John,self.Mary],'parents')
		x = self.list_names(self.Kid001.ifilter(label='Person'))
		self.assertEqual(x, 'John Mary'.split())
		x = self.list_names(self.Kid001.ifilter(label='Persona'))
		self.assertEqual(x, [])
		x = self.Kid001.iget(name='John')
		self.assertEqual(x.name, 'John')
		x = self.Kid001.iget(name='Johny')
		self.assertEqual(x, None)
		with self.assertRaises(utils.FindError):
			self.Kid001.iget(label='Person')
		self.Kid001.iremove([self.John,self.Mary])
		