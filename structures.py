from wc_utils.schema import core
import inspect

###### Structures ######
class Complex(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	def getMolecule(self,label,**kwargs):
		return self.molecules.get(label=label,**kwargs)	
	class Meta(core.Model.Meta):
		attribute_order = ('id', )

class Molecule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=False,default='Molecule')
	complex = core.ManyToOneAttribute(Complex,related_name='molecules')
	def getSite(self,label,**kwargs):
		return self.sites.get(label=label,**kwargs)
	class Meta(core.Model.Meta):
		attribute_order = ('id','label','complex', )
	
class Site(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=False,default='Site')
	molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
	class Meta(core.Model.Meta):
		attribute_order = ('id','label','molecule',)

class Bond(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	complex = core.ManyToOneAttribute(Complex,related_name='bonds')
	linkedsites = core.OneToManyAttribute(Site,related_name='bond')
	class Meta(core.Model.Meta):
		attribute_order = ('id','complex','linkedsites', )

###### Variables ######

###### Operations ######
class Operation(core.Model):
	id = core.StringAttribute(primary=True,unique=True)

class AddBond(Operation):
	label = core.StringAttribute(unique=False,default='AddBond')
	linkedsites = core.OneToManyAttribute(Site,related_name='addbond')
	
class DeleteBond(Operation):
	label = core.StringAttribute(unique=False,default='DeleteBond')
	linkedsites = core.OneToManyAttribute(Site,related_name='deletebond')
	
class AddMol(Operation):
	label = core.StringAttribute(unique=False,default='AddMol')
	mol = core.OneToOneAttribute(Molecule,related_name='addmol')

class DeleteMol(Operation):
	label = core.StringAttribute(unique=False,default='DeleteMol')
	mol = core.OneToOneAttribute(Molecule,related_name='deletemol')
	
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



def main():
	class Lig(Protein):
		label = core.StringAttribute(unique=False,default='Lig')
	class rec(ProteinSite):
		label = core.StringAttribute(unique=False,default='rec')
	class Rec(Protein):
		label = core.StringAttribute(unique=False,default='Rec')
		ph1 = core.BooleanAttribute(default=False)
		ph2 = core.BooleanAttribute(default=False)
	class lig(ProteinSite):
		label = core.StringAttribute(unique=False,default='lig')


	### Rule R1: Ligand-binding ###
	m1 = Lig(sites = [ rec(id='1'),rec(id='2') ] )
	m2 = Rec(sites = [ lig() ] )
	c1 = Complex(molecules=[m1])
	c2 = Complex(molecules=[m2])
	op = AddBond(linkedsites = [
					m1.getSite('rec',id='1'),
					m2.getSite('lig')
					])
	
	rule1 = Rule(label='R1',reactants=[c1,c2],operations=[op],reversible=True)
	
	
	### Rule R2: Crosslinking ###
	m1 = Lig(sites = [ rec(id='1'),rec(id='2') ] )
	m2 = Rec(sites = [ lig() ] )
	m3 = Rec(sites = [ lig() ] )
	b1 = Bond(linkedsites=[
				m1.getSite('rec',id='1'),
				m2.getSite('lig') 
			])
	op = AddBond(linkedsites=[
				m1.getSite('rec',id='2'),
				m3.getSite('lig') 
			])
	reac1 = Complex(molecules = [m1,m2],bonds=[b1])
	reac2 = Complex(molecules = [m3])
	rule2 = Rule(label='R2',reactants = [reac1,reac2],operations = [op],reversible=True)
	
	
if __name__ == '__main__':
	main()	

