from model import model

from pprint import pformat
from wc_rules.utils.data import DataFileUtil, NestedDict


params = model.collect_parameters()
model.verify(params)
extensions = ['yaml','json','plist','csv']

# outputs
dutil = DataFileUtil('data_out')
for ext in extensions:
	file = f'params.{ext}'
	dutil.write_file(params,file)
	d = dutil.read_file(file)
	assert NestedDict.equals(params,d)
	filepath = dutil.folder / file
	filepath.unlink()
dutil.folder.rmdir()

# complete inputs
dutil = DataFileUtil('data_hierarchical')
paramdirs = [dutil.read_file(f'params.{ext}') for ext in extensions]
assert NestedDict.equals(params,*paramdirs)

# modular inputs
dutil = DataFileUtil('data_modular')
assert NestedDict.equals(params,dutil.read_files())

# sequential inputs
dutil = DataFileUtil('data_sequential')
d1 = dutil.read_file('params.yaml')
assert NestedDict.get(d,'dephosphorylation.free_syk.dephosphorylation_rate') == 20.0

d2 = NestedDict.join(d1, dutil.read_file('edits.plist'))
model.verify(d2)
assert NestedDict.get(d2,'dephosphorylation.free_syk.dephosphorylation_rate') == 2.0


for item in NestedDict.iter_items(params):
	print(item)