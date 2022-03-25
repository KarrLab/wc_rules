from pqdict import pqdict
from collections import defaultdict
from numpy import log, seterr
from numpy.random import rand
from abc import ABC, abstractmethod

seterr(divide="ignore",invalid='ignore')


class Scheduler(ABC):

	def __init__(self):		
		self.events = pqdict()
	
	@abstractmethod
	def update(self,time,variables={}):
		# updates local state of the scheduler
		pass

	def insert(self,event,time):
		self.events[event] = time
		return self

	def pop(self):
		if len(self.events) > 0:
			event, time = self.events.popitem()
		return None, float('inf')

	
class NextReactionMethod(Scheduler):
	''' Gibson & Bruck 2000 '''

	def __init__(self):		
		super().__init__()
		self.propensities = defaultdict(float)
		
	def update(self,time,variables={}):
		for event, propensity in variables.items():
			self.propensities[event] = propensity
			tau = - log(rand()) / propensity
			self.insert(event,time + tau)
		return self

		

	
