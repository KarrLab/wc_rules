from wc_rules.pattern import Pattern
from wc_rules.utils import generate_id
from numpy.random import choice


class Species(Pattern):
    def __init__(self,idx=None,nodelist=None,recurse=True):
        if idx is None:
            idx = generate_id()
        super().__init__(idx,nodelist,recurse)


class SpeciesFactory(object):

    def __init__(self):
        self.species_dict = dict()
        self.weights_dict = dict()

    def add_species(self,species,weight=1):
        self.species_dict[species.id] = species
        self.weights_dict[species.id] = weight
        return self

    def remove_species(self,species):
        del self.species_dict[species.id]
        del self.weights_dict[species.id]

    def generate(self,n=1,preserve_ids=False):
        sorted_ids = sorted(list(self.species_dict.keys()))
        sorted_weights = [self.weights_dict[idx] for idx in sorted_ids]
        total_weight = sum(sorted_weights)
        sorted_probabilities = [x/total_weight for x in sorted_weights]
        for i in range(n):
            selection = choice(sorted_ids,p=sorted_probabilities)
            yield self.species_dict[selection].duplicate(preserve_ids=preserve_ids)
