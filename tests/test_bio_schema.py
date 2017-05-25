"""
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import bio_schema
import unittest


class TestBioSchema(unittest.TestCase):

    def test(self):
        prot = bio_schema.Protein()

        prot_site = bio_schema.ProteinSite()
        prot.add(prot_site)

        p_state = bio_schema.PhosphorylationState()
        prot_site.add(p_state)

        p_op = bio_schema.Phosphorylate()
        up_op = bio_schema.Dephosphorylate()

        p_op.set_target(p_state)
        up_op.set_target(p_state)
