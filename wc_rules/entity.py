from obj_model import core
from attrdict import AttrDict

class Entity(core.Model):
	_to = core.ManyToManyAttribute('Entity',related_name='_from')
	_props = AttrDict()
	@property
	def label(self): return self.__class__.__name__
	@property
	def id(self): return id(self)
	
	# Controls what types of entities can be added to this entity
	class EntitySignature(object):
		allowed_entity_types = tuple()
		min_allowed = dict()
		max_allowed = dict()
		
	# Controls what types of properties can be specified for this entity
	class PropertySignature(object):
		names = ('label','id',)
		allowed_types = {'label':str,'id':int}
		settable = {'label':False,'id':False}
	
	@classmethod
	def signature(cls): 
		a,min,max = cls.EntitySignature.allowed_entity_types, cls.EntitySignature.min_allowed, cls.EntitySignature.max_allowed
		temp_dict1 = {'allowed':a,'min':min,'max':max}
		
		names,types = cls.PropertySignature.names,cls.PropertySignature.allowed_types
		str1 = 'EntitySignature'
		str2 = temp_dict1.__str__()
		str3 = 'PropertySignature'
		str4 = types.__str__()
		return '\n'.join([str1,str2,str3,str4])
		
	@classmethod
	def register_new_addable(cls,cls2,min=0,max=None):
		if cls2 not in cls.EntitySignature.allowed_entity_types:
			cls.EntitySignature.allowed_entity_types += (cls2,)
		cls.EntitySignature.min_allowed[cls2] = min
		cls.EntitySignature.max_allowed[cls2] = max
	
	@classmethod
	def register_new_property(cls,name,type_ =bool,settable=True):
		cls.PropertySignature.names += (name,)
		cls.PropertySignature.allowed_types[name] = type_
		cls.PropertySignature.settable[name] = settable
	
	def __contains__(self,ent):
		return ent in self._to
	
	def append(self,ent):
		allowed_types = self.__class__.EntitySignature.allowed_entity_types
		if not isinstance(ent,allowed_types):
			raise Exception('type error')
			
		curr_length = len(self._to.filter(label=ent.label))
		max_length = self.EntitySignature.max_allowed[type(ent)]
		if curr_length >= max_length:
			raise Exception('length error')	
		self._to.append(ent)
		
	def get_property(self,name):
		if name not in self.__class__.PropertySignature.names:
			raise Exception('name error')
		return self._props.__getattr__(name)
		
	def set_property(self,name,value):
		if name not in self.__class__.PropertySignature.names:
			raise Exception('name error')
		if not self.__class__.PropertySignature.settable[name]:
			raise Exception('not settable')
		allowed_type = self.__class__.PropertySignature.allowed_types[name]
		if value is not None and not isinstance(value,allowed_type):
			raise Exception('type error')
		self._props.__setattr__(name,value)	

def main():
	pass

		
if __name__ == '__main__': 
	main()


		