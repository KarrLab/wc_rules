class Observable:

	def __init__(self,name,target,expression='target.count()'):
		self.name = name
		self.target = target
		self.expr = 'target.count()'
