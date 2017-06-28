from obj_model import core
from wc_rules import base
import wc_rules.filter as fil

class StateVariable(base.BaseClass):
	value = core.LiteralAttribute()
	filters = core.OneToManyAttribute(fil.Filter,related_name='var')
	
	def __init__(self,value=None):
		super().__init__(value=value)
		
	#### used in graph-matching ####
	def compare_values(self,value):
		if self.value is not None:
			return self.value==value
		if len(self.filters)>0:
			return all(x.does_it_match(value) for x in self.filters)
		return True
	
	
class BooleanVariable(StateVariable):
	value = core.BooleanAttribute()
	
class NumericVariable(StateVariable):
	value = core.NumericAttribute()
	
class IntegerVariable(NumericVariable):
	value = core.IntegerAttribute()
	
class FloatVariable(NumericVariable):
	value = core.FloatAttribute()
	
def main():
	pass
	
if __name__ == '__main__': 
	main()

