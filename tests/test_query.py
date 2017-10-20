from obj_model import core
from wc_rules import base
from wc_rules.query import NodeQuery
import wc_rules.graph_utils as g
import unittest
from itertools import product

class NewObject(base.BaseClass):
    prop1 = core.BooleanAttribute(default=None)
    prop2 = core.BooleanAttribute(default=None)
    class GraphMeta(g.GraphMeta):
        semantic = ('prop1','prop2')

class AnotherObject(base.BaseClass):pass

class TestBase(unittest.TestCase):
    def test_queries(self):
        # We test two queries 1x and x0 against
        # instances 00, 01, 10, 11
        nq1 = NodeQuery(query=NewObject(prop1=True,id='nq1'))
        nq2 = NodeQuery(query=NewObject(prop2=True,id='nq2'))
        queries = [nq1,nq2]

        instances = []
        for x,y in product([False,True],repeat=2):
            instances.append( NewObject(prop1=x,prop2=y) )

        # checking initial state of match_candidates and match_dict
        for nq in queries:
            self.assertEqual(len(nq.match_candidates),0)
            self.assertEqual(len(nq.match_dict),0)

        for nq in queries:
            for inst in instances:
                # these should be added
                nq.add_new_match_candidate(inst)
            # this should not be added
            nq.add_new_match_candidate( AnotherObject() )

        # checking after adding match candidates
        for nq in queries:
            self.assertEqual(len(nq.match_candidates),4)
            self.assertEqual(len(nq.match_dict),4)

        # checking if matching works properly
        nq = queries[0]
        vals = [nq.match_dict[x] for x in nq.match_candidates]
        self.assertEqual(vals,[False,False,True,True])

        nq = queries[1]
        vals = [nq.match_dict[x] for x in nq.match_candidates]
        self.assertEqual(vals,[False,True,False,True])

        # checking if updating a match works properly
        instances[3].prop1=False
        instances[3].prop2=False
        for nq in queries:
            nq.update_existing_match_candidate(instances[3])

        nq = queries[0]
        vals = [nq.match_dict[x] for x in nq.match_candidates]
        self.assertEqual(vals,[False,False,True,False])

        nq = queries[1]
        vals = [nq.match_dict[x] for x in nq.match_candidates]
        self.assertEqual(vals,[False,True,False,False])

        # checking if removing a match works properly
        for nq in queries:
            nq.remove_existing_match_candidate(instances[3])

        nq = queries[0]
        vals = [nq.match_dict[x] for x in nq.match_candidates]
        self.assertEqual(len(nq.match_candidates),3)
        self.assertEqual(vals,[False,False,True])

        nq = queries[1]
        vals = [nq.match_dict[x] for x in nq.match_candidates]
        self.assertEqual(len(nq.match_candidates),3)
        self.assertEqual(vals,[False,True,False])
