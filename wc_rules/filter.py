from obj_model import core

class Filter(core.Model):
	value = core.LiteralAttribute()
	def __init__(self,value):
		self.value = value
	
class NumericFilter(Filter):
	value = core.NumericAttribute()
class Lt(NumericFilter):	
	def get_comparison_function(self):
		return lambda x: x < self.value	
class Le(NumericFilter):
	def get_comparison_function(self):
		return lambda x: x <= self.value
class Gt(NumericFilter):	
	def get_comparison_function(self):
		return lambda x: x > self.value	
class Ge(NumericFilter):
	def get_comparison_function(self):
		return lambda x: x >= self.value
		
		
	

def main():
	a = Lt(5)
	cmp = a.get_comparison_function()
	print(cmp)
	print(cmp(4))
	print(cmp(5))
	print(cmp(6))
	print(a.validate())
	
	
if __name__ == '__main__': 
	main()
