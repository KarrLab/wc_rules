from model import model

from pprint import pformat
from wc_rules.data_utils import DataFileUtil

dutil = DataFileUtil('canonical_data')

params = model.collect_parameters()
model.verify(params)

dutil.write_file(params,'params.yaml')
params1 = dutil.read_file('params.yaml')
model.verify(params1)

dutil.write_file(params,'params.json')
params2 = dutil.read_file('params.json')
model.verify(params2)

dutil.write_file(params,'params.plist')
params3 = dutil.read_file('params.plist')
model.verify(params3)

dutil.write_file(params,'params.csv')
params4 = dutil.read_file('params.csv')
model.verify(params4)

dutil = DataFileUtil('data1')
params5 = {x:dutil.read_file(f'{x}.csv') for x in ['binding','transphosphorylation','dephosphorylation']}
model.verify(params)
