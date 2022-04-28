from wc_rules.schema.attributes import *
from wc_rules.graph.canonical_labeling import canonical_label
from wc_rules.graph.graph_partitioning import partition_canonical_form, recompose
import wc_rules.graph.examples as gex

from dataclasses import dataclass
from typing import Any
from collections import deque

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

	@parameterized.expand(graphs)
	def test_partitioning(self,name,g,syms):
		m,L,G = canonical_label(g)
		examined, to_be_examined = set(),deque([(L,G,)])

		while to_be_examined:
			L,G = to_be_examined.popleft()
			CL1,CL2 = partition_canonical_form(L,G)
			# testing that partitioning happens for all graphs with more than 1 edge
			self.assertEqual(len(L.edges)>1,CL1 is not None)
			if CL1 is not None:
				(m1,L1,G1), (m2,L2,G2) = CL1,CL2
				m3,L3,G3 = recompose(m1,L1,m2,L2)
				# testing that the recomposed graph from the partitions is the same as original
				self.assertEqual(L,L3)
				examined.add(L)
				if L2 not in examined:
					to_be_examined.appendleft((L2,G2,))
				if L1 not in examined:
					to_be_examined.appendleft((L1,G1,))

