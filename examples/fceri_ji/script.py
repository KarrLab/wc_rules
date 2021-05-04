from model import model

from pprint import pformat
from wc_rules.data_utils import DataFileUtil, compose_data

params = model.collect_parameters()
model.verify(params)

dutil = DataFileUtil('data_hierarchical')
for filename in ['params.yaml','params.json','params.plist','params.csv']:
	params = dutil.read_file(filename)
	model.verify(params)

dutil = DataFileUtil('data_modular')
params = dutil.read_files()
model.verify(params)

dutil = DataFileUtil('data_sequential')
params = compose_data(
	dutil.read_file('params.yaml'), 
	dutil.read_file('edits.plist')
	)
model.verify(params)
print(params['dephosphorylation']['free_syk'])

