from ..utils.collections import Mapping, merge_lists, remap_values, invert_dict, tuplify, index_dict
from itertools import combinations, product
from dataclasses import dataclass
from typing import Tuple
from sortedcontainers import SortedSet

def print_cycles(cycles,lb=r'(',rb=r')',sep=','):
    return ''.join([f"{lb}{sep.join(x)}{rb}" for x in cycles])

class Permutation(Mapping):

	### INSIGHT
	# if sources are sorted,
	# then x*y for any permutation will always produce
	# a permutation with sorted sources
	# However, the responsibility of sorting a permutation is elsewhere

	def cyclic_form(self,simple=False):
		values, orbits = list(self.sources), []
		while values:
			orb = [values.pop(0)]
			while values:
				t = self._dict[orb[-1]]
				if t in orb:
					break
				orb.append(t)
				values.remove(t)
			orbits.append(orb)
		if simple:
			return print_cycles(orbits)
		return tuplify(orbits)

	def is_identity(self):
		return self.sources == self.targets

	def validate(self):
		assert set(self.sources) == set(self.targets), f"{self.sources}->{self.targets} not a valid permutation."

	def duplicate(self,mapping):
		return self.__class__.create(mapping*self.sources,mapping*self.targets)


@dataclass(order=True,frozen=True)
class PermutationGroup:
	generators: Tuple[Permutation]

	@classmethod
	def create(cls,generators):
		# permutation groups always have ordered permutations
		generators = tuple(sorted([g.sort() for g in generators]))
		return PermutationGroup(generators)

	def expand(self):
		new,visited = SortedSet(self.generators), SortedSet()
		while new:
			visited |= new
			new = SortedSet([x*y for x,y in product(new,visited)]) - visited
		return list(visited)

	def validate(self):
		for x in self.generators:
			assert isinstance(x,Permutation), "Generators must be valid permutations."
			x.validate()			
		assert self.generators[0].is_identity(), f"Atleast one generator must be an identity permutation."
		
	def orbits(self,simple=False):
		orbindex = index_dict(self.generators[0].sources)
		for g in self.generators:
			for cyc in g.cyclic_form():
				if len(cyc) > 1:
					nums = [orbindex[x] for x in cyc]
					orbindex = remap_values(orbindex,nums,min(nums))	
		orbits = invert_dict(orbindex).values()
		if simple:
			return print_cycles(orbits,r'{',r'}')
		return tuplify(orbits)
		
	def iter_subgroups(self):
		# returns subgroups of self
		# a BFS exploration of the resolution diagram
		# e.g. if [0,1,2] are the generators of the group, 0 being identity
		# then iter_subgroups() yields groups:
		# [0], [0,1], [0,2], [0,1,2]

		self.validate()
		identity, remaining = self.generators[0:1], self.generators[1:]
		yield PermutationGroup(identity)
		for n in range(1,len(remaining)+1):
			for gens in combinations(remaining,n):
				yield PermutationGroup.create(identity + gens)

	def is_trivial(self):
		return len(self.generators)==1

	def duplicate(self,mapping):
		return self.__class__.create([g.duplicate(mapping) for g in self.generators])

	def pprint(self,simple=True):
		s = 'Permutation Group\n'
		for g in self.generators:
			s += str(g.cyclic_form(simple=simple)) + '\n'
		return s




