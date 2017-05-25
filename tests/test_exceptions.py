"""
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import exceptions
import unittest


class TestExceptions(unittest.TestCase):

    def test_Error(self):
        msg = 'msg'
        err = exceptions.Error(msg)
        self.assertEqual(str(err), msg)

    def test_AddObjectError(self):
        err = exceptions.AddObjectError(1., 'a', [int], method_name='test')
        msg = ('Objects of type "{}" cannot be added to objects of type "{}" using method "{}". '
               'Only objects of types {} can be added using this method.').format(
            'str', 'float', 'test', '{int}')
        self.assertEqual(str(err), msg)

    def test_RemoveObjectError(self):
        err = exceptions.RemoveObjectError(1., 'a', [int], method_name='test', not_found=False)
        msg = ('Objects of type "{}" cannot be removed from objects of type "{}" using method "{}". '
               'Only objects of types {} can be removed using this method.').format(
            'str', 'float', 'test', '{int}')
        self.assertEqual(str(err), msg)

        err = exceptions.RemoveObjectError(1., 'a', [int], method_name='test', not_found=True)
        msg = 'Object of type "{}" not found on object of type "{}"'.format('str', 'float')
        self.assertEqual(str(err), msg)
