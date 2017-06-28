from obj_model import core

class Filter(core.Model):
	value = core.LiteralAttribute()
	
	def __init__(self,value):
		super().__init__(value=value)
		
	def does_it_match(self,value):
		return self.get_comparison_function()(value)
		
	
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
	pass
	
	
if __name__ == '__main__': 
	main()
