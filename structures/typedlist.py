from collections import MutableSequence

class TypedList(MutableSequence):
	def __init__(self,allowedTypes=None,data=None):
		super(TypedList, self).__init__()
		self._list = list()
		self._allowedTypes = allowedTypes
		if data is not None:
			self.extend(data)
			
	def check(self,v):
		#  make sure there's an allowedTypes
		if not isinstance(v,self._allowedTypes):
			# if you're seeing this TypeError, 
			# you probably added the wrong type of object to a list.
			raise TypeError,"{0} is not an allowed type".format(v.__class__.__name__)
			
	def __str__(self): return str(self._list)
	def __repr__(self):
		return "TypedList {0}".format(self._list)
	def asList(self): return self._list
		
	def __len__(self): return len(self._list)
	def __getitem__(self,i): return self._list[i]
	def __delitem__(self,i): del self._list[i]
	def __setitem__(self,i,val):
		self.check(val)
		self._list[i]=val
	def insert(self,i,val):
		self.check(val)
		self._list.insert(i,val)

