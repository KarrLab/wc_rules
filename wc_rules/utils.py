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
		
###### Error ######
class AddObjectError(Exception):
	def __init__(self,parentobject,currentobject,allowedobjects,methodname='add()'):
		msg = '\nObject of ' + self.to_str(currentobject)+ ' cannot be added to ' + self.to_str(parentobject) + ' using ' + methodname + '. '
		if (len(allowedobjects)==1 or isinstance(allowedobjects,str)):
			msg = msg + 'Only objects of type' + str(allowedobjects) + 'are allowed.'
		else:
			msg = msg + 'Only objects of type ' + ', '.join(allowedobjects) + ' are allowed.'
		super(AddObjectError, self).__init__(msg)
	@staticmethod
	def to_str(obj):
		msg = str(type(obj))
		msg = ''.join([ch for ch in msg if ch not in "<>"])
		return msg