from ..utils.collections import Mapping
from dataclasses import dataclass
from typing import Tuple
from sortedcontainers import SortedSet
from collections import defaultdict

class Permutation(Mapping):

	### INSIGHT
	# if sources are sorted,
	# then x*y for any permutation will always produce
	# a permutation with sorted sources
	
	def cyclic_form(self, simple=False):
		if simple: 
			cycles = [f"({''.join(cyc)})" for cyc in self.cyclic_form()]
			return ''.join(cycles)
		d, values, cycles = self._dict, list(self.sources), []
		while values:
			s = values.pop(0)
			cyc = [s]
			while d[s] not in [s,cyc[0]]:
				cyc.append(d[s])
				values.remove(d[s])
				s = d[s]
			cycles.append(tuple(cyc))
		return tuple(cycles)

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
		generators = tuple(sorted([x.sort(canonical_order) for x in generators]))
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
		assert any([x.is_identity() for x in self.generators]), f"Atleast one generator must be an identity permutation."
		
	def orbits(self,simple=False):
		if simple:
			return ''.join([f"({''.join(x)})" for x in self.orbits()])
		cycles = set([x for g in self.generators for x in g.cyclic_form() if len(x)>1])
		orbindex = dict(zip(self.canonical_order,range(len(self.canonical_order))))
		for cyc in cycles:
			orbnums_to_merge = [orbindex[x] for x in cyc]
			elems_to_merge = [x for x in orbindex if orbindex[x] in orbnums_to_merge]
			min_orb = min(orbnums_to_merge)
			for x in elems_to_merge:
				orbindex[x] = min_orb

		orbits = []
		for num in SortedSet(orbindex.values()):
			orbits.append(tuple([x for x,numx in orbindex.items() if num==numx]))
		return tuple(orbits)

