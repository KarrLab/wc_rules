"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules.schema import base
from wc_rules.schema.attributes import *
import random
random.seed(0)

import unittest


class Person(base.BaseClass):
    name = StringAttribute()
    parents = ManyToManyAttribute('Person', max_related_rev=2, related_name='children')
    pets = OneToManyAttribute('Pet', related_name='owner')

class Pet(base.BaseClass):
    name = StringAttribute()

class TestBase(unittest.TestCase):

    def setUp(self):
        #randutils.idgen.seed(0)
        self.Sherlock = Person(name='Sherlock')
        self.John = Person(name='John')
        self.Mary = Person(name='Mary')

        self.Kid001 = Person(name='Kid001')
        self.Kid002 = Person(name='Kid002')
        self.Dog001 = Pet(name='Dog001')

    @staticmethod
    def list_names(xlist):
        return list(map((lambda x: x.name), xlist))

    def test_ids(self):
        all_things = [self.Sherlock, self.John, self.Mary, self.Kid001, self.Kid002, self.Dog001]
        id_arr = [x.id for x in all_things]
        check_str = [
        'a3f2c9bf-9c63-16b9-50f2-44556f25e2a2',
        '8d723104-f773-83c1-3458-a748e9bb17bc',
        '85776e9a-dd84-f39e-7154-5a137a1d5006',
        'eb2083e6-ce16-4dba-0ff1-8e0242af9fc3',
        '17e0aa3c-0398-3ca8-ea7e-9d498c778ea6',
        'b5d32b16-6619-4cb1-d710-37d1b83e90ec'
        ]
        self.assertEqual(id_arr, check_str)

    def test_duplicate(self):
        John2 = self.John.duplicate()
        self.assertEqual(John2.name,self.John.name)

    def test_get_connected(self):
        self.Sherlock.parents = [self.Mary, self.John]
        self.Sherlock.pets = [self.Dog001]
        self.Sherlock.children = [self.Kid001, self.Kid002]

        L = self.John.get_connected()
        self.assertEqual(len(L),6)
        self.assertEqual(set(L),set([self.Mary, self.John, self.Sherlock, self.Kid001, self.Kid002, self.Dog001]))
