import unittest
from pathlib import Path
from wc_rules.utils.data import NestedDict, DataFileUtil
import sys


class TestFceriJI(unittest.TestCase):

	def test_fceri_ji(self):
		path = Path(__file__).resolve().parent.parent / 'examples'
		sys.path.append(str(path))

		from fceri_ji.model import model
		from fceri_ji.load_data import load_hierarchical_data, load_modular_data, load_sequential_data, write_data

		params = model.collect_parameters()

		with self.assertRaises(AssertionError):
			model.verify({})

		model.verify(params)
		dicts = [*load_hierarchical_data(), load_modular_data()] 
		for d in dicts:
			self.assertEqual(params,d)
			model.verify(d)

		d = load_sequential_data()
		model.verify(d)
		
		for k,v in NestedDict.iter_items(d):
			if k==('dephosphorylation','free_syk','dephosphorylation_rate' ):
				self.assertTrue(v != NestedDict.get(params,k))
			else:
				self.assertTrue(v == NestedDict.get(params,k))


		folder = Path(__file__).resolve().parent / 'data_out'
		write_data(folder)
		extensions = ['yaml','json','plist','csv']
		dutil = DataFileUtil(folder)
		for file in [f'params.{ext}' for ext in extensions]:
			d = dutil.read_file(file)
			self.assertEqual(d,params)
			model.verify(d)
			filepath = dutil.folder / file
			filepath.unlink()
		dutil.folder.rmdir()

