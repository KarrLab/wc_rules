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
	def add_molecule(self,molecule):
		self.molecules.append(molecule)
		return self
	def add_bond(self,bond):
		self.bonds.append(bond)
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
	def add_site(self,site):
		self.sites.append(site)
		return self
	def add_exclusion(self,exclusion):
		self.exclusions.add(exclusion)
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

class Bond(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	complex = core.ManyToOneAttribute(Complex,related_name='bonds')
	linkedsites = core.OneToManyAttribute(Site,related_name='bond')
	def set_id(self,id):
		self.id = id
		return self
	def add_site(self,site):
		self.linkedsites.append(site)
		return self
	
class Exclusion(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	sites = core.ManyToManyAttribute(Site,related_name='exclusions')
	molecule = core.ManyToOneAttribute(Molecule,related_name='exclusions')
	def set_id(self,id):
		self.id = id
		return self
	def add_site(self,site):
		self.sites.append(site)
		return self

###### Variables ######
class BooleanStateVariable(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	value = core.BooleanAttribute(default=None)
	def set_id(self,id):
		self.id = id
		return self


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
	
class AddBond(Operation):
	linkedsites = core.OneToManyAttribute(Site,related_name='add_bond_op')
	@property
	def target(self): return self.linkedsites
	@target.setter
	def target(self,arr):
		self.linkedsites = arr
	def add_target_site(self,site):
		self.linkedsites.append(site)
		return self
	
class DeleteBond(Operation):
	linkedsites = core.OneToManyAttribute(Site,related_name='delete_bond_op')
	@property
	def target(self): return self.linkedsites
	@target.setter
	def target(self,arr):
		self.linkedsites = arr
	def add_target_site(self,site):
		self.linkedsites.append(site)
		return self
	
class ChangeBooleanState(Operation):
	boolvar = core.OneToOneAttribute(BooleanStateVariable,related_name='change_boolean_state_op')
	@property
	def target(self): return self.boolvar
	@target.setter
	def target(self,boolvar):
		self.boolvar = boolvar
	def set_target_var(self,boolvar):
		self.boolvar = boolvar
		return self

	
class ChangeBooleanStateToTrue(ChangeBooleanState):pass
class ChangeBooleanStateToFalse(ChangeBooleanState):pass
	
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
	def add_reactant(self,reac):
		self.reactants.append(reac)
		return self
	def add_operation(self,op):
		self.operations.append(op)
		return self
	
	
###### Structure Improvements ######
class Protein(Molecule): pass
class ProteinSite(Site): pass

###### Variable Improvements ######
class PhosphorylationState(BooleanStateVariable):
	site = core.OneToOneAttribute(Site,related_name='ph')

###### Operation Improvements ######
class Phosphorylate(ChangeBooleanStateToTrue): pass
class Dephosphorylate(ChangeBooleanStateToFalse): pass

def main():
	return
	
if __name__ == '__main__': 
	main()

