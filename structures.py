from wc_utils.schema import core
import inspect

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

class Operation(core.Model):
	id = core.StringAttribute(primary=True,unique=True)

class AddBond(Operation):
	linkedsites = core.OneToManyAttribute(Site,related_name='addbond')
	
class DeleteBond(Operation):
	linkedsites = core.OneToManyAttribute(Site,related_name='deletebond')
	
class AddMol(Operation):
	mol = core.OneToOneAttribute(Molecule,related_name='addmol')

class DeleteMol(Operation):
	mol = core.OneToOneAttribute(Molecule,related_name='deletemol')
	
class Rule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=False)
	reactants = core.OneToManyAttribute(Complex,related_name='rule')
	operations = core.OneToManyAttribute(Operation,related_name='rule')

class Protein(Molecule): pass
class ProteinSite(Site): pass

def main():
	class Lig(Protein):
		label = core.StringAttribute(unique=False,default='Lig')
	class rec(ProteinSite):
		label = core.StringAttribute(unique=False,default='rec')
	class Rec(Protein):
		label = core.StringAttribute(unique=False,default='Rec')
	class lig(ProteinSite):
		label = core.StringAttribute(unique=False,default='lig')

	x = Complex(id='1',molecules=[ Lig(sites=[rec(id='1'),rec(id='2')]) ])
	y = Complex(id='1',molecules=[ Rec(sites=[lig()]) ])
	
	op = AddBond(id='1',linkedsites=[
		x.molecules.get(label='Lig').sites.get(label='rec',id='1'),
		y.molecules.get(label='Rec').sites.get(label='lig'),
		] ) 
	
	rule1 = Rule(label='R1',reactants=[x,y],operations=[op])
	
	
	
if __name__ == '__main__':
	main()	

