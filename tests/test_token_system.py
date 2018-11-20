from wc_rules.chem import Molecule, Site,Bond
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

    def test_token_passing_01(self):
        # Tests pattern with a single node
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

        tok = token_add_node(a2)
        m.send_token(tok)
        self.assertEqual(len(n),1)

    def test_token_passing_02(self):
        # Test single-node pattern with non-matching attributes
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

    def test_token_passing_03(self):
        # Test single-node pattern with matching attributes
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

    def test_token_passing_04(self):
        # Test pattern A-X[ph=True,v=0]
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

    def test_token_passing_05(self):
        # Test pattern Ax:A(x[id=x]), X:X[id=x] with condition Ax.x in X.x
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

        tokens = [token_add_node(a001),token_add_node(x001)]
        m.send_tokens(tokens)

        x001.set_molecule(a001)
        tokens = [token_add_edge(a001,'sites','molecule',x001)]
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

    def test_token_passing_06(self):
        # Test Ax:A(X[id=x]), X:X[id=x,ph=True] with condition A.x not in X.x
        p_X = Pattern('X').add_node( X('x',ph=True) )
        p_Ax = Pattern('Ax').add_node( A('a').add_sites(X('x') ) )   \
                .add_expression('x not in X.x')

        m = Matcher()
        for p in [p_X, p_Ax]:
            m.add_pattern(p)

        #
        a001 = A()
        x001 = X(ph=True)
        tokens = [token_add_node(a001),token_add_node(x001)]
        m.send_tokens(tokens)

        x001.set_molecule(a001)
        tokens = [token_add_edge(a001,'sites','molecule',x001),]
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

    def test_token_passing_07(self):
        # Test A(<empty>)
        p1 = Pattern('p1').add_node( A('a') )
        p1.add_expression('a.sites empty')
        p2 = Pattern('p2').add_node( A('a') )

        m = Matcher()
        for p in [p1,p2]:
            m.add_pattern(p)

        self.assertEqual(m.count('p1'),0)
        self.assertEqual(m.count('p2'),0)

        # Add new A:
        a001 = A()
        tok = token_add_node(a001)
        m.send_token(tok)
        self.assertEqual(m.count('p1'),1)
        self.assertEqual(m.count('p2'),1)

        # Add new X
        x001 = X()
        tok = token_add_node(x001)
        m.send_token(tok)
        self.assertEqual(m.count('p1'),1)
        self.assertEqual(m.count('p2'),1)

        # X.set_molecule(A)
        x001.set_molecule(a001)
        tok = token_add_edge(a001,'sites','molecule',x001)
        m.send_token(tok)
        self.assertEqual(m.count('p1'),0)
        self.assertEqual(m.count('p2'),1)

        # X.unset_molecule()
        x001.unset_molecule()
        tok = token_remove_edge(a001,'sites','molecule',x001)
        m.send_token(tok)
        self.assertEqual(m.count('p1'),1)
        self.assertEqual(m.count('p2'),1)

        # Remove A
        tok = token_remove_node(a001)
        m.send_token(tok)
        self.assertEqual(m.count('p1'),0)
        self.assertEqual(m.count('p2'),0)

    def test_token_passing_08(self):
        # Test A(x)
        # One-edge
        p_Ax = Pattern('Ax').add_node( A('a').add_sites(X('x') ) )
        m = Matcher()
        for p in [p_Ax]:
            m.add_pattern(p)

        a001 = A()
        tokens = [token_add_node(a001)]
        m.send_tokens(tokens)
        n = 100
        for i in range(n):
            x = X()
            tokens = [token_add_node(x)]
            m.send_tokens(tokens)

            x.set_molecule(a001)
            tokens = [token_add_edge(x,'molecule','sites',a001)]
            m.send_tokens(tokens)

        self.assertEqual(m.count('Ax'),n)

        # Test A(x,x)
        # Two edges
        p_Axx = Pattern('Axx').add_node( A('a').add_sites( X('x1'),X('x2') ) )
        m = Matcher()
        for p in [p_Axx]:
            m.add_pattern(p)

        a001 = A()
        tokens = [token_add_node(a001)]
        m.send_tokens(tokens)
        n = 25
        for i in range(n):
            x = X()
            tokens = [token_add_node(x)]
            m.send_tokens(tokens)

            x.set_molecule(a001)
            tokens = [token_add_edge(x,'molecule','sites',a001)]
            m.send_tokens(tokens)

        self.assertEqual(m.count('Axx'),n*(n-1))

        # Three edges
        # Test A(x,x,x)
        p_Axxx = Pattern('Axxx').add_node( A('a').add_sites( X('x1'),X('x2'),X('x3') ) )
        m = Matcher()
        for p in [p_Axxx]:
            m.add_pattern(p)

        a001 = A()
        tokens = [token_add_node(a001)]
        m.send_tokens(tokens)
        n = 25
        for i in range(n):
            x = X()
            tokens = [token_add_node(x)]
            m.send_tokens(tokens)

            x.set_molecule(a001)
            tokens = [token_add_edge(x,'molecule','sites',a001)]
            m.send_tokens(tokens)

        self.assertEqual(m.count('Axxx'),n*(n-1)*(n-2))

    def test_token_passing_09(self):
        # multiple var matching
        # Test AxT:A[id=a](X[id=X,ph=True])
        # Ax:A[id=a](X[id=x])
        # with joint condition Ax.[a,x] in AxT.[a,x]
        p_AxT = Pattern('AxT').add_node( A('a').add_sites( X('x',ph=True) )  )
        p_Ax = Pattern('Ax').add_node( A('a').add_sites(X('x')) )    \
                    .add_expression('[a,x] in AxT.[a,x]')
        m = Matcher()
        for p in [p_AxT,p_Ax]:
            m.add_pattern(p)

        n=25
        for i in range(n):
            a001,x001 = A(),X(ph=True)
            tokens = [token_add_node(a001),token_add_node(x001)]
            m.send_tokens(tokens)
            x001.set_molecule(a001)
            tokens = [token_add_edge(a001,'sites','molecule',x001)]
            m.send_tokens(tokens)
        self.assertEqual(m.count('Ax'),n)

        n=25
        for i in range(n):
            a001,x001 = A(),X(ph=False)
            tokens = [token_add_node(a001),token_add_node(x001)]
            m.send_tokens(tokens)
            x001.set_molecule(a001)
            tokens = [token_add_edge(a001,'sites','molecule',x001)]
            m.send_tokens(tokens)
        self.assertEqual(m.count('Ax'),n)

        n=25
        for i in range(n):
            x001 = X(ph=True)
            tokens = [token_add_node(x001)]
            m.send_tokens(tokens)
        self.assertEqual(m.count('Ax'),n)

    def test_token_passing_10(self):
        # testing loops formed by A(x!0,x!1)
        n=10
        A_list = []
        x_right_list = []
        x_left_list = []
        for i in range(n):
            a1,xL,xR = A(),X(),X()
            a1.add_sites(xL,xR)
            A_list.append(a1)
            x_left_list.append(xL)
            x_right_list.append(xR)

        for i in range(n):
            bnd = Bond()
            x1 = x_left_list[i]
            x2 = x_right_list[i-1]
            bnd.add_sites(x1,x2)

        #pattern
        p = Pattern('loop').add_node(A_list[0])
        self.assertEqual(len(p),4*n)
        m = Matcher()
        m.add_pattern(p)

        # tokens
        tokens = []
        left = []
        right = []
        for i in range(n):
            a,xL,xR = A(),X(),X()
            left.append(xL)
            right.append(xR)
            tokens = [token_add_node(x) for x in [a,xL,xR]]
            m.send_tokens(tokens)

            a.add_sites(xL,xR)
            tokens = [token_add_edge(a,'sites','molecule',x) for x in [xL,xR]]
            m.send_tokens(tokens)

        for i in range(n):
            bnd = Bond()
            tokens = [token_add_node(bnd)]
            m.send_tokens(tokens)

            bnd.add_sites(left[i],right[i-1])
            tokens = [token_add_edge(bnd,'sites','bond',x) for x in [left[i],right[i-1]] ]
            m.send_tokens(tokens)

        self.assertEqual(m.count('loop'),2*n)
