""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
import wc_rules.utils as utils
import wc_rules.ratelaw as rl
import networkx as nx

###### Graph Methods ######
def node_match(node1,node2):
	return node2.node_match(node1)

###### Structures ######
class BaseClass(core.Model):
	"""	Base class for bioschema objects.
	Attributes:
	* id (:obj:`str`): unique id that can be used to pick object from a list
	Properties:
	* label (:obj:`str`): name of the leaf class from which object is created
	"""
	id = core.StringAttribute(primary=True,unique=True)
	class GraphMeta(core.Model.Meta):
		# outward_edges - list of RelatedManager attributes of the class
		# used in get_edges() to look for the next set of edges.
		outward_edges = tuple()
		
		# semantic - list of attributes/properties whose values
		# are checked in node_match() to compute 'semantic' equality.
		# '==' is used to compare, so they must match immutables.
		# attribute = defined using obj_model.core
		# property = defined using @property method decorator
		semantic = tuple()
	def set_id(self,id):
		""" Sets id attribute.
		Args:
			id (:obj:`str`) 
		Returns:
			self
		"""
		self.id = id
		return self
	@property
	def label(self): 
		""" Name of the leaf class from which object is created.
		"""
		return self.__class__.__name__
	
	##### Graph Methods #####
	def node_match(self,other):
		if other is None: return False
		if isinstance(other,(self.__class__,)) is not True:
			return False
		for attrname in self.__class__.GraphMeta.semantic:
			self_attr = getattr(self,attrname)
			other_attr = getattr(other,attrname)
			if self_attr is not None:
				if other_attr is None: return False
			if self_attr != other_attr: return False
		return True
	def get_edges(self):
		edges = []
		for attrname in self.__class__.GraphMeta.outward_edges:
			if getattr(self,attrname) is not None:
				attr_obj = getattr(self,attrname)
				if isinstance(attr_obj,core.RelatedManager):
					for x in attr_obj:
						edges.append(tuple([self,x]))
						edges.extend(x.get_edges())
				else:
					edges.append(tuple([self,attr_obj]))
		return edges
	

class Complex(BaseClass):
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['molecules'])
		semantic = tuple()
	def get_molecule(self,label,**kwargs):
		if label is not None:
			return self.molecules.get(label=label,**kwargs)	
		else:
			return self.molecules.get(**kwargs)
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Molecule): self.molecules.append(v)
		else: raise utils.AddObjectError(self,v,['Molecule'])
		return self
	
	
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
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Site): self.sites.append(v)
		else: raise utils.AddObjectError(self,v,['Molecule','Bond'])
		return self
	
		
class Site(BaseClass):
	molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['boolvars','pairwise_overlap','binding_state'])
		semantic = tuple()
	def add(self,v,where=None): 
		if where is None or where=='boolvars':
			return self.add_boolvars(v)
		if where=='overlaps':
			return self.add_pairwise_overlap_targets(v)
		if where=='bond':
			return self.add_bond_to(v) 
	
	#### Boolean Variables ####
	def get_boolvar(self,label,**kwargs):
		if label is not None:
			return self.boolvars.get(label=label,**kwargs)
		else:
			return self.boolvars.get(**kwargs)
	def add_boolvars(self,vars):
		for var in utils.listify(vars):
			if isinstance(var,(BooleanStateVariable,)) is not True:
				raise utils.AddObjectError(self,var,['BooleanStateVariable'])
			self.boolvars.append(var)
		return self
	
	#### Pairwise Overlaps ####
	def init_pairwise_overlap(self):
		self.pairwise_overlap = PairwiseOverlap(source=self)
		return self
	def add_pairwise_overlap_targets(self,targets,mutual=True):
		if self.pairwise_overlap is None:
			self.init_pairwise_overlap()
		if mutual==True:
			for target in targets:
				if target.pairwise_overlap is None:
					target.init_pairwise_overlap()
		self.pairwise_overlap.add_targets(targets,mutual=mutual)
		return self
	def remove_pairwise_overlap_targets(self,targets):
		return self.pairwise_overlap.remove_targets(targets)
	def undef_pairwise_overlap(self):
		targets = [t for t in self.pairwise_overlap.targets]
		self.remove_pairwise_overlap_targets(targets)
		self.pairwise_overlap = None
		return self
	def get_overlaps(self):
		if self.pairwise_overlap is None:
			return None
		if self.pairwise_overlap.n_targets == 0:
			return None
		return self.pairwise_overlap.targets
	@property
	def has_overlaps(self):
		if self.pairwise_overlap is not None:
			if self.pairwise_overlap.n_targets > 0:
				return True
		return False
		
	#### Binding State ####
	def init_binding_state(self):
		self.binding_state = BindingState(source=self)
		return self
	def add_bond_to(self,target):
		if self.binding_state is None:
			self.init_binding_state()
		if target.binding_state is None:
			target.init_binding_state()
		if self.binding_state_value is 'bound':
			raise utils.GenericError('Another bond already exists!')
		if target.binding_state_value is 'bound':
			raise utils.GenericError('Another bond already exists!')
		self.binding_state.add_targets(target)
	def remove_bond(self):
		targets = [t for t in self.binding_state.targets]
		return self.binding_state.remove_targets(targets)
	def undef_binding_state(self):
		self.remove_bond()
		self.binding_state = None
		return self
	def get_binding_partner(self):
		if self.binding_state is None:
			return None
		return self.binding_state.targets[0]
	@property
	def binding_state_value(self):
		if self.binding_state is None:
			return None
		if self.binding_state.n_targets==0:
			return 'unbound'
		if self.binding_state.n_targets==1:
			return 'bound'
		
###### Site to Site Relationships ######
class SiteRelationsManager(BaseClass):
	source = core.OneToOneAttribute(Site)
	targets = core.ManyToManyAttribute(Site)
	attrname = core.StringAttribute()
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['targets'])
		semantic = tuple()
	def add_targets(self,targets,mutual=True):
		for target in utils.listify(targets):
			self.targets.append(target)
			if mutual==True:
				getattr(target,self.attrname).add_targets([self.source],mutual=False)	
		return self
	def remove_targets(self,targets,mutual=True):
		for target in utils.listify(targets):
			self.targets.remove(target)
			if mutual==True:
				getattr(target,self.attrname).remove_targets([self.source],mutual=False)
		return self
	def get_targets(self): return self.targets
	@property
	def n_targets(self):
		if self.targets is None: return 0
		return len(self.targets)

class PairwiseOverlap(SiteRelationsManager):
	source = core.OneToOneAttribute(Site,related_name='pairwise_overlap')
	targets = core.ManyToManyAttribute(Site,related_name='pairwise_overlap_targets')
	attrname = core.StringAttribute(default='pairwise_overlap')
	
class BindingState(SiteRelationsManager):
	source = core.OneToOneAttribute(Site,related_name='binding_state')
	targets = core.ManyToManyAttribute(Site,related_name='binding_state_targets',max_related=1,max_related_rev=1)
	attrname = core.StringAttribute(default='binding_state')
	class GraphMeta(BaseClass.GraphMeta):
		outward_edges = tuple(['targets'])
		semantic = tuple(['n_targets'])
		
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
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Complex): self.reactants.append(v)
		elif isinstance(v,Operation): self.operations.append(v)
		else: raise utils.AddObjectError(self,v,['Complex','Operation'])
		return self

###### Structure Improvements ######
class Protein(Molecule): pass
class ProteinSite(Site): pass

###### Variable Improvements ######
class PhosphorylationState(BooleanStateVariable): pass

###### Operation Improvements ######
class Phosphorylate(SetTrue): pass
class Dephosphorylate(SetFalse): pass


def main():
	pass
	
if __name__ == '__main__': 
	main()

