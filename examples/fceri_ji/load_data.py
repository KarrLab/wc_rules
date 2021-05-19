from .model import model

from pprint import pformat
from wc_rules.utils.data import DataFileUtil, NestedDict

from pathlib import Path

extensions = ['yaml','json','plist','csv']
prefix = Path(__file__).resolve().parent

def load_hierarchical_data():
	dutil  = DataFileUtil(prefix / 'data' / 'hierarchical')
	return [dutil.read_file(f'params.{ext}') for ext in extensions]

def load_modular_data():
	dutil = DataFileUtil(prefix / 'data' / 'modular')
	return dutil.read_files()

def load_sequential_data():
	dutil = DataFileUtil(prefix / 'data' / 'sequential')
	#print(dutil.read_file('edits.plist'))
	return NestedDict.join(*[dutil.read_file(x) for x in ['params.yaml','edits.plist']])

def write_data(folder):
	dutil = DataFileUtil(folder)
	params = model.collect_parameters()
	for ext in extensions:
		file = f'params.{ext}'
		dutil.write_file(params,file)
	# d = dutil.read_file(file)
	# assert NestedDict.equals(params,d)





# outputs

# print(prefix)
# dutil = DataFileUtil(prefix / 'data_out')

# # complete inputs
# dutil = DataFileUtil(prefix / 'data_hierarchical')
# paramdirs = [dutil.read_file(f'params.{ext}') for ext in extensions]
# assert NestedDict.equals(params,*paramdirs)

# # modular inputs
# dutil = DataFileUtil(prefix / 'data_modular')
# assert NestedDict.equals(params,dutil.read_files())

# # sequential inputs
# dutil = DataFileUtil(prefix / 'data_sequential')
# d1 = dutil.read_file('params.yaml')
# assert NestedDict.get(d,'dephosphorylation.free_syk.dephosphorylation_rate') == 20.0

# d2 = NestedDict.join(d1, dutil.read_file('edits.plist'))
# model.verify(d2)
# assert NestedDict.get(d2,'dephosphorylation.free_syk.dephosphorylation_rate') == 2.0


# for item in NestedDict.iter_items(params):
# 	print(item)