from pqdict import pqdict
from collections import defaultdict
from numpy import array, zeros, log, seterr
from numpy.random import rand

seterr(divide="ignore",invalid='ignore')

class NextReactionMethod:
	''' Gibson & Bruck 2000 '''

	def __init__(self,time=0.0):
		
		self.absolute_time = time
		self.propensities = defaultdict(float)
		self.next_reaction_times = pqdict()

	def update_time(self,time):
		self.absolute_time = time

	def update_propensity(self,reaction,propensity):
		
		if propensity != self.propensities[reaction]:
			self.propensities[reaction] = propensity
			tau = - log(rand()) / propensity
			self.next_reaction_times[reaction] = self.absolute_time + tau
		print('Updating',reaction,propensity)
		print(self.propensities)
		print(self.next_reaction_times)
		return self			

	def next_event(self):
		reaction, time = self.next_reaction_times.topitem()
		return reaction, time


		