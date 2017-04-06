""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core

###### Structures ######
class Complex(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	def get_molecule(self,label,**kwargs):
		if label is not None:
			return self.molecules.get(label=label,**kwargs)	
		else:
			return self.molecules.get(**kwargs)
	def set_id(self,id):
		self.id = id
		return self
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Molecule): self.molecules.append(v)
		elif isinstance(v,Bond): self.bonds.append(v)
		else: assert False, AddObjectErrorMessage(self,v)
		return self
	
class Molecule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	complex = core.ManyToOneAttribute(Complex,related_name='molecules')
	@property
	def label(self): return self.__class__.__name__
	def get_site(self,label,**kwargs):
		if label is not None:
			return self.sites.get(label=label,**kwargs)
		else:
			return self.sites.get(**kwargs)
	def set_id(self,id):
		self.id = id
		return self
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Site): self.sites.append(v)
		elif isinstance(v,Exclusion): self.exclusions.append(v)
		else: assert False, AddObjectErrorMessage(self,v)
		return self
		
class Site(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
	@property
	def label(self): return self.__class__.__name__
	@property
	def bound(self):
		if self.bond is not None:
			return True
		return False
	@property
	def unbound(self): return not self.bound
	@property
	def available_to_bind(self):
		if self.unbound is False:
			return False
		if self.excludes() is not None:
			for site in self.excludes():
				if site.unbound is False:
					return False
		return True 
	def get_excludes(self):
		L = []
		for ex_obj in self.exclusions:
			for site in ex_obj.sites:
				if site is not self:	
					L.append(site)
		if len(L)>0:
			return L
		return None
	def set_id(self,id):
		self.id = id
		return self
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,BooleanStateVariable): self.boolvars.append(v)
		else: assert False, AddObjectErrorMessage(self,v)
		return self
	def get_boolvar(self,label,**kwargs):
		if label is not None:
			return self.boolvars.get(label=label,**kwargs)
		else:
			return self.boolvars.get(**kwargs)
		
		
class Bond(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	complex = core.ManyToOneAttribute(Complex,related_name='bonds')
	sites = core.OneToManyAttribute(Site,related_name='bond')
	def set_id(self,id):
		self.id = id
		return self
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Site): self.sites.append(v)
		else: assert False, AddObjectErrorMessage(self,v)
		return self
		
class Exclusion(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	sites = core.ManyToManyAttribute(Site,related_name='exclusions')
	molecule = core.ManyToOneAttribute(Molecule,related_name='exclusions')
	def set_id(self,id):
		self.id = id
		return self
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Site): self.sites.append(v)
		else: assert False, AddObjectErrorMessage(self,v)
		return self
	
###### Variables ######
class BooleanStateVariable(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	site = core.ManyToOneAttribute(Site,related_name='boolvars')
	value = core.BooleanAttribute(default=None)
	@property
	def label(self): return self.__class__.__name__
	def set_id(self,id):
		self.id = id
		return self
	def set_value(self,value):
		self.value = value
		return self
	def set_true(self): return self.set_value(True)
	def set_false(self): return self.set_value(False)
	
###### Operations ######
class Operation(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	@property
	def label(self): return self.__class__.__name__
	@property
	def target(self): return None
	@target.setter
	def target(self,value): return None
	def set_target(self,value):
		self.target = value
		return self
	def set_id(self,id):
		self.id = id
		return self
	
class BondOperation(Operation):
	sites = core.OneToManyAttribute(Site,related_name='bond_op')
	@property
	def target(self): return self.sites
	@target.setter
	def target(self,arr):
		self.sites = arr
	def set_target(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Site): self.sites.append(v)
		else: assert False, AddObjectErrorMessage(self,v,'set_target()')
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
		else: assert False, AddObjectErrorMessage(self,v)
		return self

class SetTrue(BooleanStateOperation):pass
class SetFalse(BooleanStateOperation):pass
	
##### Rule #####
class Rule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=True)
	reactants = core.OneToManyAttribute(Complex,related_name='rule')
	reversible = core.BooleanAttribute(default=False)
	operations = core.OneToManyAttribute(Operation,related_name='rule')
	def set_id(self,id):
		self.id = id
		return self
	def add(self,v):
		if type(v) is list: [self.add(w) for w in v]
		elif isinstance(v,Complex): self.reactants.append(v)
		elif isinstance(v,Operation): self.operations.append(v)
		else: assert False, AddObjectErrorMessage(self,v)
		return self

###### Error ######
def AddObjectErrorMessage(parent,obj,methodname = 'add()'):
	msg = 'Object of ' + str(type(obj))+' cannot be added to object of '+str(type(parent)) + ' using '+methodname +'.'
	msg = filter(lambda ch: ch not in "<>", msg)
	return msg
	
###### Structure Improvements ######
class Protein(Molecule): pass
class ProteinSite(Site): pass

###### Variable Improvements ######
class PhosphorylationState(BooleanStateVariable): pass

###### Operation Improvements ######
class Phosphorylate(SetTrue): pass
class Dephosphorylate(SetFalse): pass

def main():
	return
	
if __name__ == '__main__': 
	main()

