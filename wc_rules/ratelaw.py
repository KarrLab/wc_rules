from obj_model import core

import sympy
from six import integer_types, string_types, with_metaclass
#from sympy import S
#from sympy import core.all_classes as sympy_all_classes

class SymbolicExpressionAttribute(core.Attribute):
	""" Symbolic Expression to be used in RateLaws """
	def __init__(self,none=True,default=None,verbose_name='',help='Enter a Sympify-able Expression',primary=False,unique=False):
		if default is not None:
			try:
				default = sympy.S(default)
			except:
				raise ValueError('SymbolicExpressionAttribute must be either None or Sympify-able Expression')
		super(SymbolicExpressionAttribute, self).__init__(default=default,verbose_name=verbose_name,help=help,primary=primary,unique=unique)
		self.none = none
	def clean(self,value):
		if value is None:
			return (value,None)
		if value is '':
			return (value,None)
		if isinstance(value, tuple(sympy.core.all_classes)):
			return (value,None)
		if isinstance(value, string_types+integer_types+(float,)):
			return (sympy.S(value),None)

class SymbolAttribute(core.Attribute):
	def __init__(self,none=True,default=None,verbose_name='',help='Enter a Sympy Symbol',primary=True,unique=True):
		if default is not None:
			try:
				default = sympy.Symbol(default)
			except:
				raise ValueError('SymbolAttribute must be a Sympy Symbol')
		super(SymbolAttribute, self).__init__(default=default,verbose_name=verbose_name,help=help,primary=primary,unique=unique)
		self.none = none
	def clean(self,value):
		if value is None:
			return (value,None)
		if value is '':
			return (value,None)
		if isinstance(value, tuple(sympy.core.all_classes)):
			return (value,None)
		if isinstance(value, string_types):
			return (sympy.Symbol(value),None)

class Parameter(core.Model):
	symbol = SymbolAttribute(primary=True)
	value = core.FloatAttribute()

class SymbolicExpression(core.Model):
	id = core.StringAttribute(primary=True)
	expr = SymbolicExpressionAttribute()
	params = core.ManyToManyAttribute(Parameter)
	
			
def main():
	k1 = Parameter(symbol=sympy.Symbol('k1'),value=1000)
	print( k1, type(k1), k1.symbol, type(k1.symbol), )
	
	
	
if __name__ == '__main__': 
	main()
