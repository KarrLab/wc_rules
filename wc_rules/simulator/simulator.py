from ..matcher.core import build_rete_net_class
from .scheduler import NextReactionMethod
from ..utils.collections import DictLike, LoggableDict
from ..utils.data import NestedDict
from ..modeling.model import AggregateModel

class Simulator:

	ReteNetClass = build_rete_net_class()
	Scheduler = NextReactionMethod

	def __init__(self,model=None,parameters=None,**kwargs):
		# the root model is always an AggregateModel with name 'model'
		self.model = AggregateModel('model',models=[model])
	
		# parameters are encoded in "flat" mode not as NestedDict
		if parameters is None:
			parameters = dict(self.model.iter_parameters())
		else:
			parameters = dict(NestedDict.flatten(parameters))

		self.model.verify(NestedDict.unflatten(parameters))
		self.parameters = LoggableDict(parameters)
		
		# When ReteNet initialization is called
		# we MUST have compatible model and parameters
		self.net = self.ReteNetClass().initialize_start().initialize_end()
		self.net.initialize_model(self.model,self.parameters)		
		
		self.cache = DictLike()
		self.sampler = self.Scheduler()


