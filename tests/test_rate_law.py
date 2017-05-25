"""
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import rate_law
import unittest


class TestRateLaw(unittest.TestCase):

    def test_Parameter(self):
        param = rate_law.Parameter(symbol='k', value=0.1)
        self.assertEqual(param.symbol, 'k')
        self.assertEqual(param.value, 0.1)
        self.assertEqual(param.rate_expressions, [])

    def test_RateExpression(self):
        law = rate_law.RateExpression(id='Expr1', expression='k * x')
        law.parameters.create(symbol='k', value=0.1)

        param = law.parameters[0]
        self.assertEqual(param.symbol, 'k')
        self.assertEqual(param.value, 0.1)
        self.assertEqual(param.rate_expressions, [law])
