""" Test an example model

:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

from tests.fixtures import model
from wc_rules import bio_schema
import unittest


class TestModel(unittest.TestCase):

    def test(self):
        self.assertTrue(issubclass(model.schema.MetabolicEnzyme, bio_schema.Protein))
        self.assertIsInstance(model.met_enz, model.schema.MetabolicEnzyme)
