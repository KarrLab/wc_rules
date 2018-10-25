from wc_rules.chem import Molecule, Site
from wc_rules.rete_token import *
from wc_rules.matcher import Matcher
from wc_rules.pattern import Pattern
from wc_rules.attributes import *
from wc_rules.utils import *

import unittest
class A(Molecule):pass
class X(Site):
    ph = BooleanAttribute()
    v = IntegerAttribute()

class TestTokenSystem(unittest.TestCase):
    def test_token(self):
        a1 = A(id='a1')
        t1 = Token({'A':a1})
        self.assertEqual(t1['A'],a1)

        x1 = X(id='x1')
        t1['X'] = x1
        self.assertEqual(t1['X'],x1)

        s = t1.subset(['A'])
        self.assertEqual(s['A'],a1)

    def test_token_register(self):
        a1 = A(id='a1')
        x1 = X(id='x1')
        t1 = Token( { 'A':a1, 'X':x1 } )

        R = TokenRegister()
        R.add_token(t1)
        dict_to_compare = {
            ('A',a1):set([t1]),
            ('X',x1):set([t1]),
        }
        self.assertEqual(R._dict,dict_to_compare)
        self.assertEqual(R._set,set([t1]))

        R.remove_token(t1)
        self.assertEqual(len(R._dict),0)
        self.assertEqual(len(R._set),0)
        del a1,x1,t1,R

        a1,x1,x2 = A(id='a1'),X(id='x1'),X(id='x2')
        t1,t2 = Token({'a':a1,'x':x1}),Token({'a':a1,'x':x2})
        R = TokenRegister()
        for t in [t1,t2]:
            R.add_token(t)

        f1 = R.filter({'a':a1})
        self.assertEqual(len(f1),2)
        f2 = R.filter({'x':x1})
        self.assertEqual(len(f2),1)
        f3 = R.filter({'a':x1})
        self.assertEqual(len(f3),0)

    def test_token_passing_1(self):
        m = Matcher()

        a1 = A(id='a1')
        p1 = Pattern('p1').add_node(a1)
        m.add_pattern(p1)

        # currently empty
        n  = m.get_pattern('p1')
        self.assertEqual(len(n),0)

        a2 = A()

        tok = token_add_node(a2)
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_remove_node(a2)
        m.send_token(tok)
        self.assertEqual(len(n),0)

        #tok = token_edit_attrs(a2,['a','b','c'])
        #m.send_token(tok)
        #self.assertEqual(len(n),1)

        tok = token_add_node(a2)
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_remove_node(A())
        m.send_token(tok)
        self.assertEqual(len(n),1)

    def test_token_passing_2(self):
        m = Matcher()

        x1 = X(id='x1',ph=True)
        p1 = Pattern('p1').add_node(x1)
        m.add_pattern(p1)

        # currently empty
        n  = m.get_pattern('p1')
        self.assertEqual(len(n),0)

        x2 = X(ph=True,v=0)
        tok = token_add_node(x2)
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_remove_node(x2)
        m.send_token(tok)
        self.assertEqual(len(n),0)

        tok = token_edit_attrs(x2,['ph'])
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_edit_attrs(x2,['v'])
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_add_node(X(ph=False,v=0))
        m.send_token(tok)
        self.assertEqual(len(n),1)

    def test_token_passing_3(self):
        m = Matcher()

        x1 = X(id='x1',ph=True,v=0)
        p1 = Pattern('p1').add_node(x1)
        m.add_pattern(p1)

        # currently empty
        n  = m.get_pattern('p1')
        self.assertEqual(len(n),0)

        x2 = X(ph=True,v=0)
        tok = token_add_node(x2)
        m.send_token(tok)
        self.assertEqual(len(n),1)

        x2.v = 1
        tok = token_edit_attrs(x2,['v'])
        m.send_token(tok)
        self.assertEqual(len(n),0)

        x2.v = 0
        tok = token_edit_attrs(x2,['v'])
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_add_node(X(ph=False,v=0))
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_add_node(X(ph=True,v=1))
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_add_node(X(ph=True,v=0))
        m.send_token(tok)
        self.assertEqual(len(n),2)

    def test_token_passing_4(self):
        a1 = A(id='a1')
        x1 = X(id='x1',ph=True,v=0).set_molecule(a1)

        p1 = Pattern('p1').add_node(a1)

        m = Matcher()
        m.add_pattern(p1)

        n  = m.get_pattern('p1')
        self.assertEqual(len(n),0)

        a2 = A()
        x2 = X(ph=True,v=0)

        tok = token_add_node(a2)
        m.send_token(tok)
        self.assertEqual(len(n),0)

        tok = token_add_node(x2)
        m.send_token(tok)
        self.assertEqual(len(n),0)

        x2.set_molecule(a2)
        tok = token_add_edge(a2,'sites','molecule',x2)
        m.send_token(tok)
        self.assertEqual(len(n),1)

        tok = token_add_edge(a2,'sites','molecule',x2)
        m.send_token(tok)
        self.assertEqual(len(n),1)

        x2.unset_molecule()
        tok = token_remove_edge(a2,'sites','molecule',x2)
        m.send_token(tok)
        self.assertEqual(len(n),0)

        tok = token_remove_edge(a2,'sites','molecule',x2)
        m.send_token(tok)
        self.assertEqual(len(n),0)

    def test_token_passing_5(self):
        p_X = Pattern('X').add_node( X('x',ph=True) )
        p_Ax = Pattern('Ax').add_node( A('a').add_sites(X('x') ) )   \
                .add_expression('x in X.x')

        m = Matcher()
        with self.assertRaises(BuildError):
            for p in reversed([p_X, p_Ax]):
                m.add_pattern(p)

        m = Matcher()
        for p in [p_X, p_Ax]:
            m.add_pattern(p)

        #
        x001 = X(ph=True)
        a001 = A()
        x001.set_molecule(a001)

        tokens = [
            token_add_node(a001),
            token_add_node(x001),
            token_add_edge(a001,'sites','molecule',x001)
        ]

        m.send_tokens(tokens)
        self.assertEqual(m.count('X'),1)
        self.assertEqual(m.count('Ax'),1)

        #
        x001.ph = False

        tokens = [
            token_edit_attrs(x001,['ph'])
        ]

        m.send_tokens(tokens)
        self.assertEqual(m.count('X'),0)
        self.assertEqual(m.count('Ax'),0)

    def test_token_passing_6(self):
        p_X = Pattern('X').add_node( X('x',ph=True) )
        p_Ax = Pattern('Ax').add_node( A('a').add_sites(X('x') ) )   \
                .add_expression('x not in X.x')

        m = Matcher()
        for p in [p_X, p_Ax]:
            m.add_pattern(p)

        #
        a001 = A()
        x001 = X(ph=True).set_molecule(a001)
        tokens = [
            token_add_node(a001),
            token_add_node(x001),
            token_add_edge(a001,'sites','molecule',x001),
        ]
        m.send_tokens(tokens)
        self.assertEqual(m.count('X'),1)
        self.assertEqual(m.count('Ax'),0)

        #
        x001.ph = False
        tokens = [token_edit_attrs(x001,['ph'])]
        m.send_tokens(tokens)
        self.assertEqual(m.count('X'),0)
        self.assertEqual(m.count('Ax'),1)

        #
        x001.ph = True
        tokens = [token_edit_attrs(x001,['ph'])]
        m.send_tokens(tokens)
        self.assertEqual(m.count('X'),1)
        self.assertEqual(m.count('Ax'),0)



    def test_token_passing_7(self):
        p1 = Pattern('p1').add_node( A('a') )
        p1.add_expression('a.sites empty')
        p2 = Pattern('p2').add_node( A('a') )

        m = Matcher()
        for p in [p1,p2]:
            m.add_pattern(p)

        n1 = m.get_pattern('p1')
        n2 = m.get_pattern('p2')
        self.assertEqual(len(n1),0)
        self.assertEqual(len(n2),0)

        # Add new A: first add A, then null-edges
        a001 = A()
        tok = token_add_node(a001)
        m.send_token(tok)
        self.assertEqual(len(n1),0)
        self.assertEqual(len(n2),1)

        tok = token_add_null_edge(a001,'sites')
        m.send_token(tok)
        self.assertEqual(len(n1),1)
        self.assertEqual(len(n2),1)

        # Add new X
        x001 = X()
        tok = token_add_node(x001)
        m.send_token(tok)
        self.assertEqual(len(n1),1)
        self.assertEqual(len(n2),1)

        # X.set_molecule(A)
        x001.set_molecule(a001)
        tok = token_add_edge(a001,'sites','molecule',x001)
        m.send_token(tok)
        self.assertEqual(len(n1),0)
        self.assertEqual(len(n2),1)

        # X.unset_molecule()
        x001.unset_molecule()
        tok = token_remove_edge(a001,'sites','molecule',x001)
        m.send_token(tok)
        self.assertEqual(len(n1),1)
        self.assertEqual(len(n2),1)

        # Remove A: first remove null-edges, then A
        tok = token_remove_null_edge(a001,'sites')
        m.send_token(tok)
        self.assertEqual(len(n1),0)
        self.assertEqual(len(n2),1)

        tok = token_remove_node(a001)
        m.send_token(tok)
        self.assertEqual(len(n1),0)
        self.assertEqual(len(n2),0)
