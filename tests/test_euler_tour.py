from blist import blist
from wc_rules.euler_tour import EulerTour
import unittest

class TestEuler(unittest.TestCase):

    def test_reroot(self):
        x = EulerTour(None,blist([1,2,3,4,5,1]))
        x.reroot(4)
        self.assertEqual(x._tour,[4,5,1,2,3,4])
        x.reroot(1)
        self.assertEqual(x._tour,[1,2,3,4,5,1])
