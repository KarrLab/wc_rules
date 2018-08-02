from wc_rules.indexer import Index_By_ID
import pprint

class SimulationEngine(object):
    def __init__(self):
        self.simulation_state = None
        self.matcher = None

    def load_simulation_state(self,ss):
        self.simulation_state = ss
        return self

    def load_matcher(self,m):
        self.matcher = m

class SimulationState(object):

    def __init__(self):
        self._species = Index_By_ID()

    def load_new_species(self,species_list):
        for x in species_list:
            self._species.append(x)
        return self

    def __str__(self):
        s = ''
        for idx,sp in self._species.items():
            s += str(sp) +'\n'
        return s

def main():
    pass


if __name__ == '__main__':
    main()
