from ..utils.collections import Mapping, merge_lists, remap_values, invert_dict, tuplify
from itertools import combinations
from dataclasses import dataclass
from typing import Tuple

def print_cycles(cycles,lb=r'(',rb=r')'):
    return ''.join([f"{lb}{''.join(x)}{rb}" for x in cycles])

class Permutation(Mapping):

	### INSIGHT
	# if sources are sorted,
	# then x*y for any permutation will always produce
	# a permutation with sorted sources

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


@dataclass(order=True,frozen=True)
class PermutationGroup:
	generators: Tuple[Permutation]
	canonical_order: Tuple[str]

	@classmethod
	def create(cls,generators,canonical_order=None):
		if canonical_order is None:
			canonical_order = sorted(generators[0].sources)
		canonical_order = tuple(canonical_order)
		generators = tuple(sorted(set([x.sort(canonical_order) for x in generators])))	
		return PermutationGroup(generators,canonical_order)

	def expand(self):
		new,visited = set(self.generators), set()
		while new:
			visited |= new
			new = set([x*y for x in new for y in visited]) - visited
		return sorted([x.sort(self.canonical_order) for x in visited])

	def validate(self):
		for x in self.generators:
			assert isinstance(x,Permutation), "Generators must be valid permutations."
			x.validate()
			assert set(x.sources) == set(self.canonical_order), "Generators must be valid permutations."
		assert self.generators[0].is_identity(), f"Atleast one generator must be an identity permutation."
		
	def orbits(self,simple=False):
		# note: orbits are ordered by canonical order
		orbindex = dict(zip(self.canonical_order,range(len(self.canonical_order))))
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
		identity, remaining = self.generators[0], self.generators[1:]
		yield PermutationGroup((identity,), self.canonical_order)
		for n in range(1,len(remaining)+1):
			for gens in combinations(remaining,n):
				yield PermutationGroup.create((identity,) + gens, self.canonical_order)

	def is_trivial(self):
		return len(self.generators)==1



