from obj_model import core

###### Structures ######
class Complex(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	def getMolecule(self,label,**kwargs):
		if label is not None:
			return self.molecules.get(label=label,**kwargs)	
		else:
			return self.molecules.get(**kwargs)

class Molecule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	complex = core.ManyToOneAttribute(Complex,related_name='molecules')
	@property
	def label(self): return self.__class__.__name__
	def getSite(self,label,**kwargs):
		if label is not None:
			return self.sites.get(label=label,**kwargs)
		else:
			return self.sites.get(**kwargs)
	
class Site(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
	class Meta(core.Model.Meta):
		attribute_order = ('id','molecule',)
	@property
	def label(self): return self.__class__.__name__

class Bond(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	complex = core.ManyToOneAttribute(Complex,related_name='bonds')
	linkedsites = core.OneToManyAttribute(Site,related_name='bond')

###### Variables ######
class BooleanStateVariable(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	at = core.OneToOneAttribute(Site)
	value = core.BooleanAttribute(default=None)

###### Operations ######
class Operation(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	linkedsites = core.OneToManyAttribute(Site,related_name='operation')
	mol = core.OneToOneAttribute(Molecule,related_name='operation')
	boolvar = core.OneToOneAttribute(BooleanStateVariable,related_name='operation')
	complex = core.OneToOneAttribute(Complex,related_name='operation')
	@property
	def label(self): return self.__class__.__name__
	@property
	def target(self): return None


class BondOp(Operation): 
	@property
	def target(self): return self.linkedsites

class MolOp(Operation):
	@property
	def target(self): return self.mol
	
class BoolStateOp(Operation):
	@property
	def target(self): return self.boolvar
	
class AddBond(BondOp): pass
class DeleteBond(BondOp):pass
class ChangeBooleanStateToTrue(BoolStateOp): pass

##### Rule #####
class Rule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=True)
	reactants = core.OneToManyAttribute(Complex,related_name='rule')
	reversible = core.BooleanAttribute(default=False)
	operations = core.OneToManyAttribute(Operation,related_name='rule')
	
###### Structure Improvements ######
class Protein(Molecule): pass
class ProteinSite(Site): pass

###### Variable Improvements ######
class PhosphorylationState(BooleanStateVariable):
	at = core.OneToOneAttribute(Site,related_name='ph')

###### Operation Improvements ######
class Phosphorylate(ChangeBooleanStateToTrue): pass

def main():
	return
	
if __name__ == '__main__': 
	main()

