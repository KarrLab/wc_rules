from wc_rules.schema.seq import *
from wc_rules.modeling.seqpattern import OverlappingFeaturesPattern
#from wc_rules.modeling.seqpattern import build_overlap_pattern

import unittest

class Seq1(SequenceMolecule):
	pass

class Feat1(SequenceFeature):
	pass

class Feat2(SequenceFeature):
	pass


class TestOverlapPattern(unittest.TestCase):

	def test_overlap_pattern_default(self):
		overlap = OverlappingFeaturesPattern()
		ex = overlap.make_executable_expression_manager()
		match = {
			'molecule': SequenceMolecule(),
			'site1': SequenceFeature(start=1,end=4),
			'site2': SequenceFeature(start=4,end=7),
		}
		self.assertTrue(ex.exec(match) is None)

		match = {
			'molecule': SequenceMolecule(),
			'site1': SequenceFeature(start=1,end=4),
			'site2': SequenceFeature(start=7,end=4),
		}
		self.assertTrue(ex.exec(match) is None)

		match = {
			'molecule': SequenceMolecule(),
			'site1': SequenceFeature(start=1,end=5),
			'site2': SequenceFeature(start=4,end=7),
		}
		self.assertTrue(ex.exec(match) is not None)

		match = {
			'molecule': SequenceMolecule(),
			'site1': SequenceFeature(start=4,end=7),
			'site2': SequenceFeature(start=1,end=5),
		}
		self.assertTrue(ex.exec(match) is not None)

		match = {
			'molecule': SequenceMolecule(),
			'site1': SequenceFeature(start=7,end=4),
			'site2': SequenceFeature(start=1,end=5),
		}
		self.assertTrue(ex.exec(match) is not None)

	def test_overlap_pattern_build(self):
		overlap2 = OverlappingFeaturesPattern(
			molecule = Seq1('seq1'),
			site1 = Feat1('feat1'),
			site2 = Feat2('feat2')
		)

		ex = overlap2.make_executable_expression_manager()
		match = {
			'molecule': Seq1(),
			'feat1': Feat1(start=1,end=4),
			'feat2': Feat2(start=4,end=7),
		}
		self.assertTrue(ex.exec(match) is None)

		match = {
			'molecule': Seq1(),
			'feat1': Feat1(start=1,end=4),
			'feat2': Feat2(start=7,end=4),
		}
		self.assertTrue(ex.exec(match) is None)

		match = {
			'molecule': Seq1(),
			'feat1': Feat1(start=1,end=5),
			'feat2': Feat2(start=4,end=7),
		}
		self.assertTrue(ex.exec(match) is not None)

		match = {
			'molecule': Seq1(),
			'feat1': Feat1(start=4,end=7),
			'feat2': Feat2(start=1,end=5),
		}
		self.assertTrue(ex.exec(match) is not None)

		match = {
			'molecule': Seq1(),
			'feat1': Feat1(start=7,end=4),
			'feat2': Feat2(start=1,end=5),
		}
		self.assertTrue(ex.exec(match) is not None)