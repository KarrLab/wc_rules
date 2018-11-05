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

    def test_link(self):
        x1 = EulerTour('x1',blist([1]))
        x2 = EulerTour('x2',blist([2]))
        edge = tuple([1,'a','b',2])
        x1.link(x2,edge)
        self.assertEqual(x1._tour,[1,2,1])
        self.assertTrue(edge in x1._edges)
        edge = tuple([1,'c','d',2])
        x1.add_spare(edge)
        self.assertEqual(x1._tour,[1,2,1])
        self.assertTrue(edge in x1._spares)

        x3 = EulerTour('x3',blist([3]))
        edge = tuple([1,'a','b',3])
        x1.link(x3,edge)
        self.assertEqual(x1._tour,[1,2,1,3,1])
        self.assertTrue(edge in x1._edges)

        x4 = EulerTour('x4',blist([4]))
        x5 = EulerTour('x5',blist([5]))
        edge = tuple([4,'a','b',5])
        x4.link(x5,edge)
        self.assertEqual(x4._tour,[4,5,4])
        self.assertTrue(edge in x4._edges)
        edge = tuple([4,'c','d',5])
        x4.add_spare(edge)
        self.assertEqual(x4._tour,[4,5,4])
        self.assertTrue(edge in x4._spares)

        edge = tuple([2,'a','b',4])
        x1.link(x4,edge)
        self.assertEqual(x1._tour,[2,1,3,1,2,4,5,4,2])
        self.assertTrue(edge in x1._edges)
        edge = tuple([1,'c','d',2])
        self.assertTrue(edge in x1._spares)
        edge = tuple([4,'c','d',5])
        self.assertTrue(edge in x1._spares)

    def test_insert_delete(self):
        # sequentially build a tree 1,2,3,2,1
        # with two spare edges 1,2 and 2,3
        ind = EulerTourIndex()
        ind.insert_node(1)
        keys = sorted(list(ind._tourmap.keys()))
        self.assertEqual(keys,[1])
        values = set(ind._tourmap.values())
        self.assertEqual(len(values),1)

        ind.insert_node(2)
        keys = sorted(list(ind._tourmap.keys()))
        self.assertEqual(keys,[1,2])
        values = set(ind._tourmap.values())
        self.assertEqual(len(values),2)

        edge = tuple([1,'x','y',2])
        ind.insert_edge(edge)
        values = set(ind._tourmap.values())
        self.assertEqual(len(values),1)
        x = list(values)[0]
        x.reroot(1)
        self.assertEqual(x._tour,[1,2,1])

        ind.insert_node(3)
        keys = sorted(list(ind._tourmap.keys()))
        self.assertEqual(keys,[1,2,3])
        values = set(ind._tourmap.values())
        self.assertEqual(len(values),2)

        edge = tuple([2,'x','y',3])
        ind.insert_edge(edge)
        values = set(ind._tourmap.values())
        self.assertEqual(len(values),1)
        x = list(values)[0]
        x.reroot(1)
        self.assertEqual(x._tour,[1,2,3,2,1])

        # spare edges
        edge = tuple([1,'a','b',2])
        ind.insert_edge(edge)
        values = set(ind._tourmap.values())
        self.assertEqual(len(values),1)
        x = list(values)[0]
        self.assertTrue(edge in x._spares)

        edge = tuple([2,'a','b',3])
        ind.insert_edge(edge)
        values = set(ind._tourmap.values())
        self.assertEqual(len(values),1)
        x = list(values)[0]
        self.assertTrue(edge in x._spares)
