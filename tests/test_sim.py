from obj_model import core
from wc_rules.base import BaseClass
from wc_rules.query import NodeTypeQuery,NodeQuery,GraphQuery
from wc_rules.sim import SimulationState, UpdateMessage
import wc_rules.graph_utils as g
import unittest

class A(BaseClass):
    x = core.ManyToManyAttribute('A',related_name='x')
    b = core.BooleanAttribute(default=False)
    class GraphMeta(BaseClass.GraphMeta):
        semantic = ('b',)


class TestSim(unittest.TestCase):


    def test_update_scheme(self):

        # initialization
        # This a 3-clique with a boolean attribute (currently True) on each node
        instances = [A(id='inst1',b=True), A(id='inst2',b=True), A(id='inst3',b=True)]
        instances[0].x.extend([instances[1],instances[2]])
        instances[1].x.append(instances[2])

        # This is a 2-graph with True on both nodes
        queries = [A(id='query1',b=True),A(id='query2',b=True)]
        queries[0].x.append(queries[1])
        sim = SimulationState()
        # This prints out each message when received
        sim.verbose = False
        sim.add_as_graphquery(queries)

        # Test 1
        # First time adding instances
        for x in instances:
            sim.agents.append(x)
            msg = UpdateMessage(update_attr='instance',instance=x)
            sim.add_message(msg)
        sim.process_message_queue()

        # Now, it should update nodequeries and graphqueries automatically
        # Each nodequery should have three matches
        # The graphquery should have six matches
        for x in sim.nodequeries:
            self.assertEqual(len(x.matches),3)
        for x in sim.graphqueries:
            self.assertEqual(len(x.matches),6)

        # Test 2
        # make a change to an instance, check if matches update properly
        instances[2].b = False
        msg = UpdateMessage(update_attr='instance',instance=instances[2])
        sim.add_message(msg)
        sim.process_message_queue()
        # Now, each nodequery should have only two matches
        # The graphquery should have only two matches
        for x in sim.nodequeries:
            self.assertEqual(len(x.matches),2)
        for x in sim.graphqueries:
            self.assertEqual(len(x.matches),2)
