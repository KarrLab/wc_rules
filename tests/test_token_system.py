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
        self.assertEqual(a1._tokens,set([t1]))

        x1 = X(id='x1')
        t1['X'] = x1
        self.assertEqual(t1['X'],x1)
        self.assertEqual(x1._tokens,set([t1]))

        s = t1.subset(['A'])
        self.assertEqual(s['A'],a1)

        x2 = X(id='x2')
        t2 = Token({'A':a1,'X':x2})
        self.assertEqual(a1._tokens,set([t1,t2]))

        with self.assertRaises(AssertionError):
            t1.update(t2)

        t1.prep_safe_delete()
        self.assertEqual(a1._tokens,set([t2]))
        t1 = Token({'A':a1,'X':x1})
        t1.modify_with_keymap({'A':'A1','X':'X1'})

        self.assertEqual(t1._dict,{'A1':a1,'X1':x1})


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
        self.assertEqual(t1._location,R)

        R.remove_token(t1)
        self.assertEqual(len(R._dict),0)
        self.assertEqual(len(R._set),0)
        self.assertEqual(t1._location,None)
