from wc_rules.schema.seq import SequenceMolecule, SequenceFeature
from wc_rules.modeling.pattern import GraphContainer, Pattern
from wc_rules.schema.attributes import cache_method

def overlapping_sites(start1,end1,start2,end2):
	return max(start1,end1) > min(start2,end2) and max(start2,end2) > min(start1,end1)

class SequenceFeaturePattern(Pattern):

	def __init__(self,M=SequenceMolecule,S=SequenceFeature):
		g = GraphContainer(M('molecule',sites=[S('site')]).get_connected())
		super().__init__(parent=g)
		
	@cache_method
	def overlaps(cache,molecule,start,end=None):
		end = start+1 if end is None else end
		for x in cache.filter({'molecule':molecule}):
			site = x['site']
			if overlapping_sites(site.start,site.end,start,end):
				return True
		return False

class OverlappingFeaturesPattern(Pattern):

	def __init__(self,molecule=SequenceMolecule('molecule'),site1=SequenceFeature('site1'),site2=SequenceFeature('site2')):
		molecule.sites = [site1,site2]
		g = GraphContainer(molecule.get_connected())
		s1,s2 = site1.id, site2.id
		constraints = [
			f'max({s1}.start,{s1}.end) > min({s2}.start,{s2}.end)',
			f'max({s2}.start,{s2}.end) > min({s1}.start,{s1}.end)',
		]
		super().__init__(parent=g,constraints=constraints)

# # Note that we're using Python-style 0-indexing for sequences
# # so end - start = length
# # Also, this works irrespective of the orientation of the 
# # site, i.e., start > end or start < end