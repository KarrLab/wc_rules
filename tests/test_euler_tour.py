from blist import blist
from wc_rules.euler_tour import EulerTour
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
        x.delete_sequence(0,2)
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])
        x.extend_right([0,1])
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1,0,1])
        x.delete_sequence(9,2)
        self.assertEqual(x._tour,[1,2,3,4,5,4,3,2,1])
