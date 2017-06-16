""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
import wc_rules.ratelaw as rl
import wc_rules.graph_utils as g
from wc_rules.base import BaseClass
import wc_rules.utils as utils

class Complex(BaseClass):
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['molecules'])
		semantic = tuple()
	def get_molecule(self,label,**kwargs):
		if label is not None:
			return self.molecules.get(label=label,**kwargs)	
		else:
			return self.molecules.get(**kwargs)
	
	
class Molecule(BaseClass):
	complex = core.ManyToOneAttribute(Complex,related_name='molecules')
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['sites'])
		semantic = tuple()
	def get_site(self,label,**kwargs):
		if label is not None:
			return self.sites.get(label=label,**kwargs)
		else:
			return self.sites.get(**kwargs)
		
class Site(BaseClass):
	molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
	bond = core.OneToOneAttribute('Site',related_name='bond')
	overlaps = core.ManyToManyAttribute('Site',related_name='overlaps')
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['bond','overlaps','boolvars'])
		semantic = tuple()
	
	#### Boolean Variables ####
	def get_boolvar(self,label,**kwargs):
		if label is not None:
			return self.boolvars.get(label=label,**kwargs)
		else:
			return self.boolvars.get(**kwargs)
	
	#### Pairwise Overlaps ####
	def add_overlaps(self,other_sites,mutual=True):
		return self.add_by_attrname(other_sites,'overlaps')

	def remove_overlaps(self,other_sites):
		return self.remove_by_attrname(other_sites,'overlaps')
	
	def undef_overlaps(self):
		self.overlaps = None
		return self 
		
	def get_overlaps(self):
		return self.overlaps
		
	@property
	def has_overlaps(self):
		return self.overlaps is not None
		
	#### Binding State ####
	def undef_binding_state(self):
		self.bond = None
		return self
	def add_unbound_state(self):
		self.bond = self
		return self
	def add_bond_to(self,target):
		for x in [self,target]:
			x.undef_binding_state()
		self.bond = target
		return self
	def remove_bond(self):
		other = self.bond
		for x in [self,other]:
			x.undef_binding_state()
			x.add_unbound_state()
		return self
	@property
	def binding_state_value(self):
		if self.bond is None: return None
		elif self.bond is self: return 'unbound'
		else: return 'bound'
	
	def get_binding_partner(self):
		if self.bond is not None:
			if self.bond is self:
				return None
		return self.bond
		
###### Variables ######
class BooleanStateVariable(BaseClass):
	site = core.ManyToOneAttribute(Site,related_name='boolvars')
	value = core.BooleanAttribute(default=None)
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple()
		semantic = tuple(['value'])
	def set_value(self,value):
		self.value = value
		return self
	def set_true(self): return self.set_value(True)
	def set_false(self): return self.set_value(False)
	
###### Operations ######
class Operation(BaseClass):
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['target'])
		semantic = tuple()
	@property
	def target(self): return None
	@target.setter
	def target(self,value): return None
	def set_target(self,value): 
		self.target = value
		return self

class BondOperation(Operation):
	sites = core.OneToManyAttribute(Site,related_name='bond_op')
	@property
	def target(self): return self.sites
	@target.setter
	def target(self,arr):
		self.sites = arr
	def set_target(self,v):
		if type(v) is list: [self.set_target(w) for w in v]
		elif isinstance(v,Site): self.sites.append(v)
		else: raise utils.AddObjectError(self,v,['Site'],'set_target()')
		return self
	
class AddBond(BondOperation):pass
class DeleteBond(BondOperation):pass

class BooleanStateOperation(Operation):
	boolvar = core.OneToOneAttribute(BooleanStateVariable,related_name='boolean_state_op')
	@property
	def target(self): return self.boolvar
	@target.setter
	def target(self,boolvar):
		self.boolvar = boolvar
	def set_target(self,v):
		if isinstance(v,BooleanStateVariable): self.boolvar = v
		else: raise utils.AddObjectError(self,v,['BooleanStateVariable'],'set_target()')
		return self

class SetTrue(BooleanStateOperation):pass
class SetFalse(BooleanStateOperation):pass
	
##### Rule #####
class Rule(BaseClass):
	reactants = core.OneToManyAttribute(Complex,related_name='rule')
	reversible = core.BooleanAttribute(default=False)
	operations = core.OneToManyAttribute(Operation,related_name='rule')
	forward = core.OneToOneAttribute(rl.RateExpression,related_name='rule_forward')
	reverse = core.OneToOneAttribute(rl.RateExpression,related_name='rule_reverse')
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['reactants','operations'])
		semantic = tuple()

def main():
	pass
if __name__ == '__main__': 
	main()

