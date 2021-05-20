"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules.schema import base
from wc_rules.schema.attributes import *
from wc_rules.utils import random as randutils

import unittest


class Person(base.BaseClass):
    name = StringAttribute()
    parents = ManyToManyAttribute('Person', max_related_rev=2, related_name='children')
    pets = OneToManyAttribute('Pet', related_name='owner')

class Pet(base.BaseClass):
    name = StringAttribute()

class TestBase(unittest.TestCase):

    def setUp(self):
        randutils.idgen.seed(0)
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
            'e3e70682-c209-4cac-629f-6fbed82c07cd',
            'f728b4fa-4248-5e3a-0a5d-2f346baa9455',
            'eb1167b3-67a9-c378-7c65-c1e582e2e662',
            'f7c1bd87-4da5-e709-d471-3d60c8a70639',
            'e443df78-9558-867f-5ba9-1faf7a024204',
            '23a7711a-8133-2876-37eb-dcd9e87a1613',
        ]
        # works only when utils.idgen.seed(0) in setUp()
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
