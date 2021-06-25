from wc_rules.schema.attributes import *
from wc_rules.graph.canonical_labeling import canonical_label
import wc_rules.graph.examples as gex

from dataclasses import dataclass
from typing import Any

import unittest
from parameterized import parameterized

@dataclass(frozen=True,eq=True)
class CanonicalLabelBuild:
	mapping: Any
	labeling: Any
	group: Any

graphs = [(k,*v) for k,v in gex.gen_all_graphs().items()]
class TestCanonicalLabel(unittest.TestCase):
	@parameterized.expand(graphs)
	def test_graph(self,name,g,nsyms):
		build0 = CanonicalLabelBuild(*canonical_label(g))

		# reconstruct g as g1 using build0.mapping
		# prove g1==g, i.e. build(g1) == build(g)
		g1 = build0.labeling.build_graph_container(build0.mapping)
		build1 = CanonicalLabelBuild(*canonical_label(g1))
		self.assertEqual(build0.mapping,build1.mapping)
		self.assertEqual(build0.labeling,build1.labeling)

		# construct a canonical graph g2 equivalent to g
		# build(g2) should have identity mapping 
		# but same canonical form as build1
		g2 = build0.labeling.build_graph_container()
		build2 = CanonicalLabelBuild(*canonical_label(g2))
		self.assertEqual(build2.mapping.sources, build2.mapping.targets)
		self.assertEqual(build0.labeling,build2.labeling)

		# permutation group relations
		# build0 and build1 must have an identical permgroup
		# since they are built from the same graph
		self.assertEqual(build0.group,build1.group)

		# build0.group and build2.group must be equivalent in expansion
		# but are not guaranteed to have the same generator-form
		p0,p2 = [x.group.expand() for x in [build0,build2]]
		self.assertEqual(p0,p2)

		# the expanded-form must have the expected number of permutations
		self.assertEqual(len(p0),nsyms)

		# count_symmetries (orb-stab theorem) must give the expected num of permutations
		self.assertEqual(build0.group.count_symmetries(),nsyms)
