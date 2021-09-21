from ..schema.molecules import *
from ..schema.sites import *
from wc_rules.modeling.pattern import GraphContainer

def build_ligand(n_fc=2):
	assert n_fc in [1,2]
	if n_fc == 2:
		classes = [Ligand,FcBind,FcBind]
		names = 'ligand fc_1 fc_2'.split()
		edges = [x.split() for x in ['ligand sites fc_1', 'ligand sites fc_2']]
	elif n_fc == 1:
		classes = [Ligand,FcBind]
		names = 'ligand fc'.split()
		edges = ['ligand sites fc'.split()]
	return GraphContainer.initialize_from(classes,names,edges)

def build_receptor(contents=['alpha', 'beta', 'gamma']):
	classes, names, edges = [Receptor], ['receptor'], []
	if 'alpha' in contents:
		classes.append(Alpha)
		names.append('alpha')
		edges.append('receptor sites alpha'.split())
	if 'beta' in contents:
		classes.append(Beta)
		names.append('beta')
		edges.append('receptor sites beta'.split())
	if 'gamma'  in contents:
		classes.append(Gamma)
		names.append('gamma')
		edges.append('receptor sites gamma'.split())
	return GraphContainer.initialize_from(classes,names,edges)

def build_Lyn():
	return GraphContainer.initialize_from([Lyn, SH2],['lyn','sh2'],['lyn sites sh2'.split()])

def build_Syk(contents=['tsh2','linker','aloop']):
	classes, names, edges = [Syk], ['syk'], []
	if 'tsh2' in contents:
		classes.append(TandemSH2)
		names.append('tsh2')
		edges.append('syk sites tsh2'.split())
	if 'linker' in contents:
		classes.append(LinkerRegion)
		names.append('linker')
		edges.append('syk sites linker'.split())
	if 'aloop' in contents:
		classes.append(ActivationLoop)
		names.append('aloop')
		edges.append('syk sites aloop'.split())
	return GraphContainer.initialize_from(classes,names,edges)

def recruit_to_receptor(gReceptor,gRecruit):
	if 'lyn' in gRecruit._dict:
		gReceptor['beta'].bond = gRecruit['sh2']
	if 'syk' in gRecruit._dict:
		gReceptor['gamma'].bond = gRecruit['tsh2']
	return gReceptor + gRecruit

def recruit_to_ligand(n_fc,g1,g2=None):
	g = build_ligand(n_fc)
	if n_fc==1:
		assert g2 is None
		g['fc'].bond = g1['alpha']
	if n_fc==2:
		g1 = g1.add_suffix('1')
		g['fc_1'].bond = g1['alpha_1']
		if g2:
			g2 = g2.add_suffix('2')
			g['fc_2'].bond = g2['alpha_2']
	return GraphContainer(g['ligand'].get_connected())

def add_phosphosite_to_molecule(g,molname):
	g[molname].sites.add(PhosphoSite('phosphosite'))
	return GraphContainer(g[molname].get_connected())	