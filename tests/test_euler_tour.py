from blist import blist
from wc_rules.euler_tour import EulerTour,EulerTourIndex
import itertools
import unittest

class TestEuler(unittest.TestCase):

    def test_reroot(self):
        x = EulerTour(None,blist([1,2,3,4,5,4,3,2,1]))
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])
        x.reroot(4)
        self.assertEqual(x._tour,[4,5,4,3,2,1,2,3,4])
        x.reroot(1)
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])

    def test_insert_delete(self):
        x = EulerTour(None,blist([1,2,3,4,5,4,3,2,1]))
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])
        x.insert_sequence(5,[6,7,6,5])
        self.assertEqual(x._tour,[1,2,3,4,5,6,7,6,5,4,3,2,1])
        x.delete_sequence(idx=5,length=4)
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])
        x.extend_left([1,0])
        self.assertEqual(x._tour,[1,0,1,2,3,4,5,4,3,2,1])
        x.shrink_left(2)
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])
        x.extend_right([0,1])
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1,0,1])
        x.shrink_right(2)
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])

    def test_eulertourindex(self):
        ind = EulerTourIndex()

        x = EulerTour('x',blist([1,2,3,4,5,4,3,2,1]))

        ind.add_tour(x)
        self.assertEqual(sorted(ind._tourmap.keys()),[1,2,3,4,5])
        for key in [1,2,3,4,5]:
            self.assertEqual(ind.get_mapped_tour(key),x)

        x._tour = blist([1,2,3,2,1,6,7,6,1])
        ind.edit_tour(x,removed_nodes=[4,5],added_nodes=[6,7])
        self.assertEqual(sorted(ind._tourmap.keys()),[1,2,3,6,7])
        for key in [1,2,3,6,7]:
            self.assertEqual(ind.get_mapped_tour(key),x)

        for i,j in itertools.combinations([1,2,3,6,7],2):
            self.assertTrue(ind.is_connected([i,j]))

        ind.remove_tour(x)
        for key in range(10):
            self.assertEqual(ind.get_mapped_tour(key),None)
