from wc_utils.schema import core
import inspect

class Complex(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	class Meta(core.Model.Meta):
		attribute_order = ('id', )

class Molecule(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=False)
	complex = core.ManyToOneAttribute(Complex,related_name='molecules')
	class Meta(core.Model.Meta):
		attribute_order = ('id','label','complex', )
	
class Site(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	label = core.StringAttribute(unique=False)
	molecule = core.ManyToOneAttribute(Molecule,related_name='sites')
	class Meta(core.Model.Meta):
		attribute_order = ('id','label','molecule',)

class Bond(core.Model):
	id = core.StringAttribute(primary=True,unique=True)
	complex = core.ManyToOneAttribute(Complex,related_name='bonds')
	linkedsites = core.OneToManyAttribute(Site,related_name='bond')
	class Meta(core.Model.Meta):
		attribute_order = ('id','complex','linkedsites', )
	

class Protein(Molecule): pass
class ProteinSite(Site): pass

def main():
	class Lig(Protein):pass
	class rec(ProteinSite):pass
	class Rec(Protein):pass
	class lig(ProteinSite):pass

	x = Lig(id='1',sites=[rec(),rec()])
	y = Rec(id='2',sites=[lig(),lig()])
	z = Complex(molecules=[x,y])

	print z
	print z.molecules
	print z.molecules.filter(id='1')
	print z.molecules.filter(id='2')
	
if __name__ == '__main__':
	main()	

