from obj_model import core
from wc_rules import base
from wc_rules.query import NodeTypeQuery,NodeQuery,GraphQuery
import wc_rules.graph_utils as g
import unittest
from itertools import product

# used for test_nodequery
class NewObject(base.BaseClass):
    prop1 = core.BooleanAttribute(default=None)
    prop2 = core.BooleanAttribute(default=None)
    class GraphMeta(g.GraphMeta):
        semantic = ('prop1','prop2')

class AnotherObject(base.BaseClass):pass

# used for test_nodetypequery
class A(base.BaseClass):pass
class B(A):pass
class C(base.BaseClass):pass
class D(C):pass

# used for test_graphquery_compile_nodequeries
class A1(base.BaseClass):
	b = core.OneToOneAttribute('B1',related_name='a')
	c = core.OneToManyAttribute('C1',related_name='a')
	d = core.ManyToManyAttribute('D1',related_name='a')
class B1(base.BaseClass):pass
class C1(base.BaseClass):pass
class D1(base.BaseClass):pass

# used for testing graph isomorphism
class A2(base.BaseClass):
    b = core.OneToOneAttribute('B2',related_name='a')
class B2(base.BaseClass):pass



class TestQuery(unittest.TestCase):
    def test_nodetypequery(self):
        ntq = NodeTypeQuery()
        for x in [A(id='nqA'), B(id='nqB'), D(id='nqD'), C(id='nqC')]:
            nq = NodeQuery(query=x)
            ntq.register_new_nq(nq)

        instances = [A(id='instA'), B(id='instB'), C(id='instC'), D(id='instD')]
        compares = [['nqA'],['nqA','nqB'],['nqC'],['nqC','nqD']]
        for x,y in zip(instances,compares):
            vec = ntq[x.__class__]
            cmp = sorted([z.query.id for z in vec])
            self.assertEqual(cmp,y)


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

    def test_graphquery_compile_nodequeries(self):
        a_vec = [A1(),A1()]
        b_vec = [B1()]
        c_vec = [C1(),C1()]
        d_vec = [D1(),D1()]

        a_vec[0].b = b_vec[0]
        a_vec[1].c.extend(c_vec)
        a_vec[0].d.extend(d_vec)
        a_vec[1].d.extend(d_vec)
        abcd = a_vec+b_vec+c_vec+d_vec
        gq = GraphQuery()

        for i,x in enumerate(abcd):
        	name = 'nq'+str(i)
        	gq.add_nodequery( NodeQuery(query=x,id=name) )
        gq.compile_traversal_functions()

        str1_arr = []
        for nq in gq.nodequeries:
            str1_arr.append(' '.join(['from',nq.id,'to',*[x.id for x in nq.next_nq]]))
        str2_arr = ['from nq0 to nq2 nq5 nq6','from nq1 to nq3 nq4 nq5 nq6',
        'from nq2 to nq0','from nq3 to nq1','from nq4 to nq1','from nq5 to nq0 nq1',
        'from nq6 to nq0 nq1']
        self.assertEqual(str1_arr,str2_arr)
        return

    def test_graph_isomorphism(self):

        # query graph
        a1 = A2(id='a1')
        b1 = B2(id='b1')
        a1.b = b1
        gq = GraphQuery(id='gq')
        gq.add_nodequery( NodeQuery(query=a1,id='nq_a1') )
        gq.add_nodequery( NodeQuery(query=b1,id='nq_b1') )
        gq.compile_traversal_functions()

        # instance graph
        a2 = A2(id='a2')
        b2 = B2(id='b2')
        a2.b = b2
        for nq in gq.nodequeries:
            for m in [a2,b2]:
                nq.update_match(m)

        nq_instance_tuplist = list(zip(gq.nodequeries,[a2,b2]))
        gq.update_for_new_nodequery_matches(nq_instance_tuplist)
        self.assertEqual(len(gq.matches),1)
        return
