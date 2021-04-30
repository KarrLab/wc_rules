from model import model

from pprint import pformat
from wc_rules.data_utils import DataFileUtil

dutil = DataFileUtil('canonical_data')

params = model.collect_parameters()
model.verify(params)

params1 = model.collect_parameters()
model.verify(params1)

dutil.write_file(params1,'params.yaml')
params2 = dutil.read_file('params.yaml')
model.verify(params2)

dutil.write_file(params1,'params.json')
params3 = dutil.read_file('params.json')
model.verify(params3)

dutil.write_file(params1,'params.plist')
params4 = dutil.read_file('params.plist')
model.verify(params4)

