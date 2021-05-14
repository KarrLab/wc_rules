from copy import deepcopy
import json, csv, io
import yaml

from pathlib import Path
from collections import defaultdict, Counter

class NestedDict:
	# static methods for working with Nested Dicts
	# assumes keys are all strings
	
	@staticmethod
	def resolve_path(key):
		if isinstance(key,str):
			return tuple(key.split('.'))
		return key

	@staticmethod
	def get(d,key):
		try:
			for elem in NestedDict.resolve_path(key):
				d = d[elem]
		except:
			raise KeyError(f'Could not resolve key {key}')
		return d

	@staticmethod
	def set(d,key,value):
		path = NestedDict.resolve_path(key)
		for elem in path[:-1]:
			if elem not in d or not isinstance(d[elem],dict):
				d[elem] = dict()
			d = d[elem]
		d[path[-1]] = value
		return

	# iter_items takes a dict and yields items
	# compose takes items and yields a dict
	@staticmethod
	def iter_items(d,mode='tuple'):
		if mode=='tuple':
			for k,v in d.items():
				if isinstance(v,dict):
					for k1,v1 in NestedDict.iter_items(v):
						yield (k,*k1),v1
				else:
					yield (k,),v
		if mode=='str':
			for k,v in NestedDict.iter_items(d):
				yield '.'.join(k),v

	@staticmethod
	def compose(*items):
		outd = dict()
		for k,v in items:
			NestedDict.set(outd,k,v)
		return outd

	@staticmethod
	def join(*dicts):
		return NestedDict.compose(*[item for d in dicts for item in NestedDict.iter_items(d)])

	@staticmethod
	def equals(*dicts):
		d0_items = sorted(NestedDict.iter_items(dicts[0]))
		for d in dicts[1:]:
			if sorted(NestedDict.iter_items(d)) != d0_items:
				return False
		return True

DELIMITER = ','

class YAMLUtil:
	# Represents nested dict as is.

	@staticmethod
	def read(s):
		return yaml.load(s)

	@staticmethod
	def write(d):
		return yaml.dump(d,default_flow_style=False)

class JSONUtil:
	# Represents nested dict as is.

	@staticmethod
	def read(s):
		return json.loads(s)

	@staticmethod
	def write(d):
		return json.dumps(d,indent=4)

class PLISTUtil:
	# Simplifies nested dict to flat dict.

	@staticmethod
	def read(s):
		L = list(csv.reader(s.splitlines(), delimiter=DELIMITER, quoting = csv.QUOTE_NONNUMERIC))
		return NestedDict.compose(*L)

	@staticmethod
	def write(d):
		rows = [['.'.join(k),v] for k,v in NestedDict.iter_items(d)]
		s = io.StringIO()
		w = csv.writer(s, delimiter=DELIMITER, quoting = csv.QUOTE_NONNUMERIC)
		w.writerows(rows)
		return s.getvalue()

class CSVUtil:
	# Leaf keys are grouped and arranged in columns
	# Non-leaf keys are flattened and treated as row names with column header "model"
	# E.g. {'x':{'m': {'a': 1, 'b': 2}, 'n': {'b': 3, 'c': 4}}}
	# ==> 
	# model, a, b, c
	#   x.m, 1, 2,''
	#   x.n,'', 3, 4

	@staticmethod
	def read(s):
		elems = list(csv.reader(s.splitlines(), delimiter=DELIMITER,  quoting = csv.QUOTE_NONNUMERIC))
		headers = elems.pop(0)[1:]
		items = [(f'{elem[0]}.{h}',v) for elem in elems for h,v in zip(headers,elem[1:]) if v!='']
		return NestedDict.compose(*items)

	@staticmethod
	def write(d):
		fieldnames,csvd = dict(model=1), defaultdict(dict)
		for k, v in NestedDict.iter_items(d):
			model,param = '.'.join(k[:-1]), k[-1]
			csvd[model]['model'] = model
			csvd[model][param] = v
			fieldnames[param] = 1
		
		s = io.StringIO()
		w = csv.DictWriter(s,delimiter=DELIMITER, fieldnames = fieldnames.keys(), quoting = csv.QUOTE_NONNUMERIC)
		w.writeheader() 
		w.writerows(csvd.values())
		return s.getvalue()


class DataFileUtil:

	utils = {
		'yaml': YAMLUtil,
		'json': JSONUtil,
		'plist': PLISTUtil,
		'csv': CSVUtil
	}

	def __init__(self,folder='.'):
		self.folder = Path(folder)

	def read_file(self,filename):
		file = self.folder / filename
		data_format = file.suffix[1:]
		txt = file.read_text()
		data = self.utils[data_format].read(txt)
		return data
		
	def write_file(self,data,filename):
		file = self.folder / filename
		data_format = file.suffix[1:]
		txt = self.utils[data_format].write(data)
		self.folder.mkdir(parents=True,exist_ok=True)
		file.write_text(txt)
		return
	
	def read_files(self,filenames=[]):
		if filenames == []:
			files = sorted(self.folder.glob('*.*'))
		else:
			files = [self.folder / x for x in filenames]
		return {file.stem:self.read_file(file.name) for file in files}



