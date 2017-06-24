from obj_model import core
import wc_rules.filter as fil


	
class BooleanVariable(core.StateVariable):
	value = core.BooleanAttribute()
	
class NumericVariable(core.StateVariable):
	value = core.NumericAttribute()
	
class IntegerVariable(NumericVariable):
	value = core.IntegerAttribute()
	
class FloatVariable(NumericVariable):
	value = core.FloatAttribute()
	
def main():
	a = StateVariable()
	print(len(a.filters))
	
	
if __name__ == '__main__': 
	main()

