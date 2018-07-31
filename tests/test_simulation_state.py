from wc_rules.chem import Molecule,Site
from wc_rules.species import Species,SpeciesFactory
from wc_rules.engine import SimulationState
from obj_model import core
import unittest
from collections import Counter

class A(Molecule):pass
class X(Site):
    ph1 = core.BooleanAttribute(default=None)
    ph2 = core.BooleanAttribute(default=None)


class TestSimulationState(unittest.TestCase):

    def test_simulation_state(self):
        s1 = Species('s1').add_node( A(id='a').add_sites(X(id='x',ph1=False,ph2=False)) )
        s2 = Species('s2').add_node( A(id='a').add_sites(X(id='x',ph1=True,ph2=False)) )
        s3 = Species('s3').add_node( A(id='a').add_sites(X(id='x',ph1=False,ph2=True)) )
        s4 = Species('s4').add_node( A(id='a').add_sites(X(id='x',ph1=True,ph2=True)) )

        sf = SpeciesFactory()
        for x in [s1,s2,s3,s4]:
            sf.add_species(x,weight=1)

        ss =SimulationState().load_new_species(list(sf.generate(100,preserve_ids=True)))

        c = sum(s._nodes['x'].ph1 and s._nodes['x'].ph2 for x,s in ss._species.items())
        self.assertTrue(c < 50)
        c = sum(s._nodes['x'].ph1 or s._nodes['x'].ph2 for x,s in ss._species.items())
        self.assertTrue(c > 50)
