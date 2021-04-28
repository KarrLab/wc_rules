
from schema_molecules import *
from schema_sites import *

from wc_rules.pattern import GraphContainer
from pprint import pprint

x = Ligand('ligand', sites=[
		FcBind('fc1'), 
		FcBind('fc2')
	])
gLigand = GraphContainer(x.get_connected())

x = Receptor('receptor',sites=[
	Alpha('alpha'), 
	Beta('beta'), 
	Gamma('gamma')
	])
gReceptor = GraphContainer(x.get_connected())

x = Lyn('lyn',sites=[SH2('sh2')])
gLyn = GraphContainer(x.get_connected())

x = Syk('syk',sites=[
		TandemSH2('tsh2'),
		ActivationLoop('aloop'),
		LinkerRegion('linker')
	])
gSyk = GraphContainer(x.get_connected())

# graphs for binding rules
gReceptorAlpha = GraphContainer(gReceptor.duplicate(include=['receptor','alpha']))
gReceptorBeta = GraphContainer(gReceptor.duplicate(include=['receptor','beta']))
gReceptorGamma = GraphContainer(gReceptor.duplicate(include=['receptor','gamma']))


x = gReceptorBeta.duplicate()['beta']
y = gLyn.duplicate()['sh2']
x.bond = y
gLynReceptor = GraphContainer(x.get_connected())

gSykTsh2 = gSyk.duplicate(include=['syk','tsh2'])

# graphs for building dimers
x = gReceptorGamma.duplicate()['gamma']
y = gSykTsh2.duplicate()['tsh2']
x.bond = y
gSykReceptor = GraphContainer(x.get_connected())

g1,glyn,gsyk = gReceptor.duplicate(), gLyn.duplicate(), gSyk.duplicate()
rec, beta, gamma = g1['receptor'], g1['beta'], g1['gamma']
sh2, tsh2 = glyn['sh2'], gsyk['tsh2']
beta.bond = sh2
gamma.bond = tsh2
gFullMonomer = GraphContainer(rec.get_connected())


glig = gLigand.duplicate()
lig, fc1, fc2 = glig['ligand'], glig['fc1'], glig['fc2']
g1, g2 = gFullMonomer.add_suffix('left'), gFullMonomer.add_suffix('right')

alpha1, alpha2 = g1['alpha_left'], g2['alpha_right']
fc1.bond = alpha1
fc2.bond = alpha2
gFullDimer = GraphContainer(lig.get_connected())

# graphs for transphosphorylation
dimer_components = ['ligand','fc1','fc2','receptor_left','alpha_left','receptor_right','alpha_right']

lyn_components = dimer_components + ['beta_left','lyn_left','sh2_left']
gLynOnBeta = gFullDimer.duplicate(include= lyn_components + ['beta_right'])
gLynOnGamma = gFullDimer.duplicate(include= lyn_components + ['gamma_right'])

lyn_on_syk_components = lyn_components + ['gamma_right','syk_right','tsh2_right']
gLynOnSykALoop = gFullDimer.duplicate(include= lyn_on_syk_components + ['aloop_right'])
gLynOnSykLinker = gFullDimer.duplicate(include= lyn_on_syk_components + ['linker_right'])

syk_components = dimer_components + ['gamma_left','gamma_right','tsh2_left', 'tsh2_right', 'syk_left','syk_right','aloop_left','aloop_right']
gSykOnSyk = gFullDimer.duplicate(include = syk_components)


# graphs for dephosphorylation
# Receptor
x = Receptor('receptor',sites=[PhosphoSite('phosphosite')])
gRecPhospho = GraphContainer(x.get_connected())

# Syk
x = Syk('syk',sites=[TandemSH2('tsh2'), PhosphoSite('phosphosite')])
gSykPhospho = GraphContainer(x.get_connected())