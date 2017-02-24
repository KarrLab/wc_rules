from collections import MutableSequence

class TypedList(MutableSequence):
	def __init__(self,allowedTypes,*args):
		super(TypedList,self).__init__()
		self._allowedTypes = allowedTypes
		self._list = list()
		if args is not None:
			self.extend(args)
	
	def check(self,v):
		if not isinstance(v,self._allowedTypes):
			# # if you're seeing this TypeError, 
			# # you probably added the wrong type of object to a list.
			raise TypeError,"Object type {0} not allowed in this list.".format(v.__class__.__name__)
	
	def __len__(self): return len(self._list)
	def __getitem__(self,i): return self._list[i]
	def __delitem__(self,i): del self._list[i]
	def __setitem__(self,i,val):
		self.check(val)
		self._list[i]=val
	def insert(self,i,val):
		self.check(val)
		self._list.insert(i,val)
	def __repr__(self): 
		str1 = sel
		return "TypedList {0} {1}".format(self._allowedTypes,self._list)
	def asList(self): return self._list
