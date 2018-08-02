"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import base
from wc_rules import graph_utils
from wc_rules import utils
from obj_model import core
import unittest


class Person(base.BaseClass):
    name = core.StringAttribute()
    parents = core.ManyToManyAttribute('Person', max_related_rev=2, related_name='children')
    pets = core.OneToManyAttribute('Pet', related_name='owner')

    class GraphMeta(graph_utils.GraphMeta):
        outward_edges = ('children', 'pets')
        semantic = ('name',)


class Pet(base.BaseClass):
    name = core.StringAttribute()


class TestBase(unittest.TestCase):

    def setUp(self):
        utils.idgen.seed(0)
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

    def test_attribute_properties(self):
        attrprops = self.John.attribute_properties
        keylist = 'id name parents pets children'.split()
        for x in keylist:
            self.assertTrue(list(attrprops.keys()))
        check_dict = {
            'id': {'related': False, 'append': False},
            'name': {'related': False, 'append': False},
            'parents': {'related': True, 'append': True},
            'pets': {'related': True, 'append': True},
            'children': {'related': True, 'append': True},
        }
        for x in check_dict:
            for y in ['related', 'append']:
                self.assertEqual(attrprops[x][y], check_dict[x][y])

        self.assertEqual(attrprops['id']['related_class'], None)
        self.assertEqual(attrprops['name']['related_class'], None)
        self.assertEqual(attrprops['parents']['related_class'], type(self.John))
        self.assertEqual(attrprops['pets']['related_class'], type(self.Dog001))
        self.assertEqual(attrprops['children']['related_class'], type(self.Kid001))

        self.assertEqual(attrprops['parents']['related_attr'],'children')
        self.assertEqual(attrprops['children']['related_attr'],'parents')
        self.assertEqual(attrprops['pets']['related_attr'],'owner')

    def test_duplicate(self):
        John2 = self.John.duplicate()
        self.assertEqual(John2.name,self.John.name)
