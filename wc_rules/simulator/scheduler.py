from pqdict import pqdict
from collections import defaultdict
from numpy import log, seterr
#from numpy.random import rand
import random
from abc import ABC, abstractmethod
from sortedcontainers import SortedSet

seterr(divide="ignore",invalid='ignore')


class Scheduler:

	def __init__(self):		
		self.events = pqdict()

	def peek(self):
		if len(self.events) > 0:
			event,time = self.events.topitem()
			return event,time
		return None, float('inf')
	
	def update(self,time,variables={}):
		# updates local state of the scheduler
		return self

	def insert(self,time,event):
		self.events[event] = time
		return self

	def pop(self):
		if len(self.events) > 0:
			event,time = self.events.popitem()
			return event,time
		return None, float('inf')

class RepeatedEventScheduler(Scheduler):

	def __init__(self, event, period, start=0.0):
		super().__init__()
		self.event = event
		self.period = period
		self.insert(start,self.event)

	def pop(self):
		event,time = Scheduler.pop(self)
		if event is not None:
			self.insert(time+self.period,self.event)
		return event,time

class CoordinatedScheduler(Scheduler):

	def __init__(self,schedulers):
		self.schedulers = schedulers

	def pop(self):
		events = SortedSet()
		for i,x in enumerate(self.schedulers):
			event,time = x.peek()
			if event is not None:
				events.add((time,event,i))
		if len(events) > 0:
			time,event, i = events[0]
			return self.schedulers[i].pop()
		return None, float('inf')

	def peek(self):
		events = SortedSet()
		for i,x in enumerate(self.schedulers):
			event,time = x.peek()
			if event is not None:
				events.add((time,event,i))
		if len(events) > 0:
			time,event, i = events[0]
			return event,time
		return None, float('inf')


	def update(self,time,variables={}):
		for sch in self.schedulers:
			sch.update(time,variables)
		return self

class NextReactionMethod(Scheduler):
	''' Gibson & Bruck 2000 '''

	def __init__(self):		
		super().__init__()
		self.propensities = defaultdict(float)

	def update(self,time,variables={}):
		for var, value in variables.items():
			if var.endswith('.propensity'):
				event = '.'.join(var.split('.')[:-1])
				self.propensities[event] = value
				self.schedule(time,event)
		return self

	def schedule(self,time,event):
		assert event in self.propensities
		propensity = self.propensities[event]
		tau = - log(random.random()) / propensity
		self.insert(time + tau,event)
		return self

	def pop(self):
		event,time =  Scheduler.pop(self)
		self.schedule(time,event)
		return event,time


