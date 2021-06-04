from ..utils.collections import Mapping, merge_lists, remap_values, invert_dict, tuplify
from dataclasses import dataclass
from typing import Tuple

def get_cycles(d):
    values, orbits = list(d.keys()), []
    while values:
        orb = [values.pop(0)]
        while values:
            t = d[orb[-1]]
            if t in orb:
                break
            orb.append(t)
            values.remove(t)
        orbits.append(orb)
    return tuplify(orbits)

def print_cycles(cycles):
    return ''.join([f"{{{''.join(x)}}}" for x in cycles])

class Permutation(Mapping):

	### INSIGHT
	# if sources are sorted,
	# then x*y for any permutation will always produce
	# a permutation with sorted sources

	def cyclic_form(self,simple=False):
		if simple:
			return print_cycles(self.cyclic_form())
		return get_cycles(dict(zip(self.sources,self.targets)))

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
		assert any([x.is_identity() for x in self.generators]), f"Atleast one generator must be an identity permutation."
		
	def orbits(self,simple=False):
		# note: orbits are ordered by canonical order
		if simple:
			return print_cycles(self.orbits())

		cycles = set([x for g in self.generators for x in g.cyclic_form() if len(x)>1])
		orbindex = dict(zip(self.canonical_order,range(len(self.canonical_order))))
		for cyc in cycles:
			orbnums = [orbindex[x] for x in cyc]
			orbindex = remap_values(orbindex,orbnums,min(orbnums))
		orbits = tuplify(invert_dict(orbindex).values())
		return orbits
		
	def iter_subgroups(self):
		self.validate()


