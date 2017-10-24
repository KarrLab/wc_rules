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

class TestQuery(unittest.TestCase):
    def test_nodequery(self):
        # We test two queries 1x and x1 against
        # instances 00, 01, 10, 11
        nq1 = NodeQuery(query=NewObject(prop1=True,id='nq1'))
        nq2 = NodeQuery(query=NewObject(prop2=True,id='nq2'))
        queries = [nq1,nq2]

        instances = []
        for x,y in product([False,True],repeat=2):
            instances.append( NewObject(prop1=x,prop2=y) )

        # checking initial state
        for nq in queries:
            self.assertEqual(len(nq.matches),0)

        # updating 4 correct matches and 1 incorrect match
        for nq in queries:
            for inst in instances:
                # these should be added
                nq.update_match(inst)
            # this should not be added
            nq.update_match( AnotherObject() )

        # checking number of matches
        for nq in queries:
            self.assertEqual(len(nq.matches),2)

        # checking if updating a match works properly
        instances[3].prop1=False
        instances[3].prop2=False
        for nq in queries:
            nq.update_match(instances[3])

        for nq in queries:
            self.assertTrue(instances[3] not in nq)
        return
