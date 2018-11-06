from blist import blist
from wc_rules.euler_tour import EulerTour,EulerTourIndex
from wc_rules.chem import Molecule, Site, Bond
import unittest

class A(Molecule):pass
class X(Site):pass


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

    def test_create_delete_new_tour(self):
        ind = EulerTourIndex()
        a = A()
        ind.create_new_tour_from_node(a)
        self.assertTrue(ind.get_mapped_tour(a) is not None)
        ind.delete_existing_tour_from_node(a)
        self.assertTrue(ind.get_mapped_tour(a) is None)

    def test_link(self):
        t1 = EulerTour('t1',[9,8,5,6,7,6,5,8,9])
        t2 = EulerTour('t2',[4,2,1,2,3,2,4])

        ind = EulerTourIndex()
        ind.add_new_tour(t1)
        ind.add_new_tour(t2)

        t,n = t1,[5,6,7,8,9]
        self.assertTrue(all([ind.get_mapped_tour(x)==t for x in n]))
        t,n = t2,[1,2,3,4]
        self.assertTrue(all([ind.get_mapped_tour(x)==t for x in n]))

        x1 = ind.link(t1,t2,5,1)
        self.assertEqual(x1._tour,[5,6,7,6,5,8,9,8,5,1,2,3,2,4,2,1,5])

    def test_cut(self):
        t1 = EulerTour('t1',[1,2,3,2,4,2,1,5,6,7,6,5,8,9,8,5,1])
        ind = EulerTourIndex()
        ind.add_tour(t1)

        x1,x2 = ind.cut(t1,1,5)
        self.assertEqual(x1._tour,[5,6,7,6,5,8,9,8,5])
        self.assertEqual(x2._tour,[1,2,3,2,4,2,1])

    def test_auglink(self):
        ind = EulerTourIndex()

        a1,x1,x2,a2 = A(),X(),X(),A()
        for n in [a1,x1,a2,x2]:
            ind.create_new_tour_from_node(n)
        self.assertEqual(len(ind),4)

        for a,x in [[a1,x1],[a2,x2]]:
            x.set_molecule(a)
            e = tuple([x,'molecule','sites',a])
            ind.auglink(e)
        self.assertEqual(len(ind),2)

        bnd = Bond()
        ind.create_new_tour_from_node(bnd)
        self.assertEqual(len(ind),3)

        for x in [x1,x2]:
            bnd.add_sites(x)
            e = tuple([x,'bond','sites',bnd])
            ind.auglink(e)
        self.assertEqual(len(ind),1)

        # Complex is now A-X-bnd-X-A
        # lets add another A-X-bnd-X-A with the same A's to test add-spaare
        x3,x4 = X(),X()
        for a,x in [[a1,x3],[a2,x4]]:
            ind.create_new_tour_from_node(x)
            x.set_molecule(a)
            e = tuple([x,'molecule','sites',a])
            ind.auglink(e)
        self.assertEqual(len(ind),1)

        bnd = Bond()
        ind.create_new_tour_from_node(bnd)
        for x in [x3,x4]:
            bnd.add_sites(x)
            e = tuple([x,'bond','sites',bnd])
            ind.auglink(e)
        self.assertEqual(len(ind),1)
        self.assertEqual(len(list(ind)[0]._spares),1)

    def test_augcut(self):
        # Create A-X-bnd-X-A-X-bnd-X-A loop, where first & last A's are same
        ind = EulerTourIndex()
        a1,a2,x1,x2,x3,x4 = A('a1'), A('a2'), X('x1'), X('x2'), X('x3'), X('x4')
        for n in [a1,a2,x1,x2,x3,x4]:
            ind.create_new_tour_from_node(n)
        for a,x in [[a1,x1],[a2,x2],[a1,x3],[a2,x4]]:
            x.set_molecule(a)
            e = tuple([x,'molecule','sites',a])
            ind.auglink(e)
        bnd1,bnd2 = Bond('bnd1'),Bond('bnd2')
        for i,j,bnd in [[x1,x2,bnd1],[x3,x4,bnd2]]:
            ind.create_new_tour_from_node(bnd)
            for k in [i,j]:
                bnd.add_sites(k)
                e = tuple([k,'bond','sites',bnd])
                ind.auglink(e)
        self.assertEqual(len(ind),1)
        self.assertEqual(len(list(ind)[0]._spares),1)

        # test cutting a bridge when there is a spare
        # i.e., cutting x1,bnd,x2 and x3,bnd,x4 should compensate
        bnd = x1.bond
        for x in [x1,x2]:
            x.unset_bond()
            e = tuple([x,'bond','sites',bnd])
            ind.augcut(e)
        ind.delete_existing_tour_from_node(bnd)
        self.assertEqual(len(ind),1)
        self.assertEqual(len(list(ind)[0]._spares),0)
