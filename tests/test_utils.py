"""
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import utils
import unittest


class TestUtils(unittest.TestCase):

    def test_Factory(self):
        factory = utils.Factory()
        names = ['ClassA', 'ClassB']

        instances = factory.build(object, names, create_instances=True)
        self.assertEqual([obj.__class__.__name__ for obj in instances], names)

        classes = factory.build(object, names, create_instances=False)
        self.assertTrue(all([isinstance(cls, type) for cls in classes]))
        self.assertEqual([cls.__name__ for cls in classes], names)

    def test_listify(self):
        self.assertEqual(utils.listify(1.), [1.])
        self.assertEqual(utils.listify([1.]), [1.])
        self.assertEqual(utils.listify([1., 2.]), [1., 2.])
