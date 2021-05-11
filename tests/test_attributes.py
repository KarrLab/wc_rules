from wc_rules.schema.attributes import *
from wc_rules.schema.base import BaseClass
import unittest


class X(BaseClass):
    b = BooleanAttribute()
    f = FloatAttribute()
    i = IntegerAttribute()
    pi = PositiveIntegerAttribute()
    s = StringAttribute()

    @computation
    def product(f,i,factor=1):
        return f*i*factor

class TestAttributes(unittest.TestCase):

    def test_attribute_defaults(self):
        x1 = X('idx1')
        self.assertEqual(x1.id,'idx1')
        self.assertEqual(x1.b,None)
        self.assertEqual(x1.f,None)
        self.assertEqual(x1.i,None)
        self.assertEqual(x1.pi,None)
        self.assertEqual(x1.s,None)


    def test_computation_decorator(self):
        x1 = X(id='idx1',b=True,f=0.5,i=100)

        self.assertTrue(x1.product._is_computation)
        self.assertEqual(x1.product(),50)
        self.assertEqual(x1.product(factor=3),150)
        self.assertEqual(x1.product(f=0.25,factor=3),75)
        self.assertEqual(x1.product(f=0.25,i=10,factor=3),7.5)
