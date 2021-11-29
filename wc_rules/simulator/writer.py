

class Writer:

	def __init__(self,time=0.0):
		self.previous = time
		self.current = time

	def update(self,time):
		self.previous, self.current = self.current, time
		return self

