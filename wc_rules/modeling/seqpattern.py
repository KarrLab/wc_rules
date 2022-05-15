from wc_rules.schema.seq import SequenceMolecule, SequenceFeature
from wc_rules.modeling.pattern import GraphContainer, Pattern

def build_overlap_pattern(**kwargs):
	assert len(kwargs)==0 or sorted(kwargs.keys()) == ['molecule','site1','site2']
	molecule = kwargs.get('molecule',SequenceMolecule('molecule'))
	site1 = kwargs.get('site1',SequenceFeature('site1'))
	site2 = kwargs.get('site2',SequenceFeature('site2'))
	s1 = site1.id
	s2 = site2.id
	molecule.sites = [site1,site2]
	return Pattern(
		parent = GraphContainer(molecule.get_connected()),
		constraints = [
			f'max({s1}.start,{s1}.end) > min({s2}.start,{s2}.end)',
			f'max({s2}.start,{s2}.end) > min({s1}.start,{s1}.end)',
		]
	)

default_overlap_pattern = build_overlap_pattern()

# Note that we're using Python-style 0-indexing for sequences
# so end - start = length
# Also, this works irrespective of the orientation of the 
# site, i.e., start > end or start < end