from core import WorkingMemoryGraph
from wc_rules.chem import Molecule,Site
from obj_model.core import BooleanAttribute

from random import random
import pprint

def boolgen(): return random() < 0.5

class A(Molecule):pass

class X(Site):
    ph1 = BooleanAttribute(default=False)
    ph2 = BooleanAttribute(default=False)


def object_generator(n=1):
    for i in range(n):
        yield A().add_sites( X( ph1=boolgen(), ph2=boolgen() ) )


list_of_molecules = object_generator(5)

'''
for i in list_of_molecules:
    print(i.label, i.id)
    for x in i.sites:
        print(x.label,x.id,x.ph1,x.ph2)
    print('')
'''

wmg = WorkingMemoryGraph()
for molec in list_of_molecules:
    wmg.add_node(molec)
    for site in molec.sites:
        wmg.add_node(site)

pprint.pprint(wmg.nodes)
