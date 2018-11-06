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

        x = EulerTour(None,blist([1,2,3,2,4,2,1,5,6,7,6,5,8,9,8,5,1]))
        x.reroot(4)
        self.assertEqual(x._tour,[4,2,1,5,6,7,6,5,8,9,8,5,1,2,3,2,4])
        x.reroot(6)
        self.assertEqual(x._tour,[6,7,6,5,8,9,8,5,1,2,3,2,4,2,1,5,6])
        x.reroot(1,2)
        self.assertEqual(x._tour,[1,2,3,2,4,2,1,5,6,7,6,5,8,9,8,5,1])
        x.reroot(1,5)
        self.assertEqual(x._tour,[1,5,6,7,6,5,8,9,8,5,1,2,3,2,4,2,1])

    def test_extend_shrink(self):
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

    def test_first_last(self):
        x = EulerTour(None,blist([1,2,3,7,3,4,5,4,3,2,1]))
        self.assertEqual(x.first_occurrence(1),0)
        self.assertEqual(x.last_occurrence(1),10)
        self.assertEqual(x.first_occurrence(7),3)
        self.assertEqual(x.last_occurrence(7),3)
        self.assertEqual(x.first_occurrence(5),6)
        self.assertEqual(x.last_occurrence(5),6)
        self.assertEqual(x.first_occurrence(3),2)
        self.assertEqual(x.last_occurrence(3),8)
        self.assertEqual(x.first_occurrence(8),None)
        self.assertEqual(x.last_occurrence(8),None)


    def test_link(self):
        t1 = EulerTour('t1',[9,8,5,6,7,6,5,8,9])
        t2 = EulerTour('t2',[4,2,1,2,3,2,4])

        ind = EulerTourIndex()
        ind.add_tour(t1)
        ind.add_tour(t2)

        t,n = t1,[5,6,7,8,9]
        self.assertTrue(all([ind.get_mapped_tour(x)==t for x in n]))
        t,n = t2,[1,2,3,4]
        self.assertTrue(all([ind.get_mapped_tour(x)==t for x in n]))

        b1 = ind.link(t1,t2,5,1)
        self.assertEqual(b1,[5,6,7,6,5,8,9,8,5,1,2,3,2,4,2,1,5])


    def test_cut(self):
        t1 = EulerTour('t1',[1,2,3,2,4,2,1,5,6,7,6,5,8,9,8,5,1])
        ind = EulerTourIndex()
        ind.add_tour(t1)

        b1,b2 = ind.cut(t1,1,5)
        self.assertEqual(b1,[5,6,7,6,5,8,9,8,5])
        self.assertEqual(b2,[1,2,3,2,4,2,1])
