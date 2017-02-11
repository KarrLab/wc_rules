class Bond(list): 
	def __init__(self,listobj):
		assert (len(listobj) <= 2), "Bond must be a list of size 2" 
		super(Bond,self).__init__(listobj)

