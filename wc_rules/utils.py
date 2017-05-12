###### Factory ######
class Factory(object):
	def build(self,obj_type,names,instances=True):
		types = dict()
		vec = []
		for name in names:
			if name not in moltypes:
				types[name] = type(name,(obj_type,),{})
				if instances==False:
					vec.append( types[name] )
			if instances==True:
				vec.append( types[name]() )
		return vec
		
###### Methods ######
def listify(value): 
	if type(value) is not list: return [value]
	return value
		
###### Error ######
class GenericError(Exception):
	def __init__(self,msg=None):
		if msg is None: msg=''
		super(GenericError, self).__init__(msg)
		
class AddObjectError(Exception):
	def __init__(self,parentobject,currentobject,allowedobjects,methodname='add()'):
		msg = '\nObject of type ' + self.to_str(currentobject)+ ' cannot be added to ' + self.to_str(parentobject) + ' using ' + methodname + '. '
		if (len(allowedobjects)==1 or isinstance(allowedobjects,str)):
			msg2 = str(allowedobjects)
		else:
			msg2 = ', '.join(allowedobjects)
		msg = msg + 'Only objects of type ' + msg2 + ' are allowed for this method.' 
		super(AddObjectError, self).__init__(msg)
	@staticmethod
	def to_str(obj):
		msg = str(type(obj))
		msg = ''.join([ch for ch in msg if ch not in "<>"])
		return msg

class RemoveObjectError(Exception):
	def __init__(self,parentobject,currentobject,allowedobjects,methodname='remove()',notfound=False):
		if notfound==False:
			msg = '\nObject of type ' + self.to_str(currentobject)+ ' cannot be removed from ' + self.to_str(parentobject) + ' using ' + methodname + '. '
			if (len(allowedobjects)==1 or isinstance(allowedobjects,str)):
				msg2 = str(allowedobjects)
			else:
				msg2 = ', '.join(allowedobjects)
			msg = msg + 'Only objects of type ' + msg2 + ' are allowed for this method.' 
		else:
			msg = '\nObject ' + self.to_str(currentobject) + ' not found!'
		super(AddObjectError, self).__init__(msg)
	@staticmethod
	def to_str(obj):
		msg = str(type(obj))
		msg = ''.join([ch for ch in msg if ch not in "<>"])
		return msg
