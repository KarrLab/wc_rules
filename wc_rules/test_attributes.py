from wc_rules.attributes import *
from wc_rules.base import BaseClass

import unittest


class X(BaseClass):
    b = BooleanAttribute()
    f = FloatAttribute()
    i = IntegerAttribute()
    pi = PositiveIntegerAttribute()
    s = StringAttribute()


class TestAttributes(unittest.TestCase):

    def test_attribute_defaults(self):
        x1 = X(id='idx1')
        self.assertEqual(x1.id,'idx1')
        self.assertEqual(x1.b,None)
        self.assertEqual(x1.f,None)
        self.assertEqual(x1.i,None)
        self.assertEqual(x1.pi,None)
        self.assertEqual(x1.s,None)
