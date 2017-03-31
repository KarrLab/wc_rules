from obj_model import core

###### Structures ######
class Complex(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	def getMolecule(self,label,**kwargs):
		if label is not None:
			return self.molecules.get(**kwargs)	
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

###### Operations ######
class Operation(core.Model):
	id = core.StringAttribute(primary=True,unique=True)

class AddBond(Operation):
	linkedsites = core.OneToManyAttribute(Site,related_name='addbond')
	@property
	def label(self): return self.__class__.__name__
	
class DeleteBond(Operation):
	linkedsites = core.OneToManyAttribute(Site,related_name='deletebond')
	@property
	def label(self): return self.__class__.__name__
	
class AddMol(Operation):
	mol = core.OneToOneAttribute(Molecule,related_name='addmol')
	@property
	def label(self): return self.__class__.__name__

class DeleteMol(Operation):
	mol = core.OneToOneAttribute(Molecule,related_name='deletemol')
	@property
	def label(self): return self.__class__.__name__
	
class Rule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=True)
	reactants = core.OneToManyAttribute(Complex,related_name='rule')
	operations = core.OneToManyAttribute(Operation,related_name='rule')
	reversible = core.BooleanAttribute(default=False)
	
###### Structure Improvements ######
class Protein(Molecule): pass
class ProteinSite(Site): pass

###### Variable Improvements ######

###### Operation Improvements ######



	
if __name__ == '__main__': pass	

