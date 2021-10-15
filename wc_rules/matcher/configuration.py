from types import MethodType
from .initialize import default_initialization_methods
from .functionalize import default_functionalization_methods
from collections import ChainMap

default_kwargs = dict(
	initialization_methods = default_initialization_methods,
	functionalization_methods = default_functionalization_methods
	)

class ReteNetConfiguration:

	def __init__(self,**kwargs):
		self.config = kwargs
		for k,v in kwargs.items():
			if k not in self.config:
				self.config[k]=v

	def configure(self,net,overwrite=False):
		for k,methods in self.config.items():
			for method in methods:
				m = MethodType(method, net)
				assert overwrite or method.__name__ not in dir(self)
				setattr(net,method.__name__,m)		
		return net

def default_configuration():
	return ReteNetConfiguration(**default_kwargs)
