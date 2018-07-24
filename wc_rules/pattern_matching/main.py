from core import WorkingMemoryGraph, AlphaTree,Pattern
from wc_rules.chem import Molecule,Site
from obj_model.core import BooleanAttribute

import random
import pprint

def boolgen(): return random.random() < 0.5

class A(Molecule):pass

class X(Site):
    ph1 = BooleanAttribute(default=None)
    ph2 = BooleanAttribute(default=None)


def object_generator(n=1):
    for i in range(n):
        yield A().add_sites( X( ph1=boolgen(), ph2=boolgen() ) )


list_of_molecules = object_generator(5)
wmg = WorkingMemoryGraph()
for molec in list_of_molecules:
    wmg.add_node(molec)
    for site in molec.sites:
        wmg.add_node(site)

a1 = A(id='a').add_sites(X(id='x',ph1=True))
patt1 = Pattern('p1').add_nodes([a1])

a2 = A(id='a').add_sites(X(id='x',ph2=True))
patt2 = Pattern('p2').add_nodes([a2])

a3 = A(id='a').add_sites(X(id='x',ph1=True,ph2=True))
patt3 = Pattern('p3').add_nodes([a3])


typecheck_tree = AlphaTree().add_patterns([patt1,patt2,patt3])

for idx,instance in wmg.nodes.items():
    typecheck_tree.process_token(instance,verbose=True)
    print()
#pprint.pprint(a1.sites[0].attribute_properties)
