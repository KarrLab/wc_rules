
from wc_rules.chem import Site
from wc_rules.attributes import BooleanAttribute

class PhosphoSite(Site):
	ph = BooleanAttribute()

# Ligand
class FcBind(Site):
	pass

# Receptor
class Alpha(Site):
	pass

class Beta(PhosphoSite):
	pass

class Gamma(PhosphoSite):
	pass

# Lyn
class SH2(Site):
	pass

# Syk
class TandemSH2(Site):
	pass

class LinkerRegion(PhosphoSite):
	pass

class ActivationLoop(PhosphoSite):
	pass
