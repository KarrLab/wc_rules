from wc_rules.chem import Molecule, Site
from wc_rules.rete_token import Token, TokenRegister
import unittest
class A(Molecule):pass
class X(Site):pass

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

        x2 = X(id='x2')
        t2 = Token({'A':a1,'X':x2})

        with self.assertRaises(AssertionError):
            t1.update(t2)

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
