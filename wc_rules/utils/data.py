from copy import deepcopy
import json, csv, io
import yaml

from pathlib import Path
from collections import defaultdict, Counter

class NestedDict:
	# static methods for working with Nested Dicts
	# assumes keys are all strings
	
	@staticmethod
	def convert_to_pathtuple(s):
		assert isinstance(s,(str,tuple)), f"Key {s} must be a string (e.g., `a.b.c`) or tuple (e.g., ('a','b','c',))."
		if isinstance(s,str):
			return tuple(s.split('.'))
		return s

	@staticmethod
	def convert_to_pathstring(t):
		return '.'.join(t)

	@staticmethod
	def get(d,key):
		path =  NestedDict.convert_to_pathtuple(key)
		for elem in path:
			d = d[elem]
		return d

	@staticmethod
	def make_path(d,path):
		for elem in path:
			if not isinstance(d.get(elem,None), dict):
				d[elem] = dict()
			d = d[elem]
		return d

	@staticmethod
	def set(d,key,value):
		path = NestedDict.convert_to_pathtuple(key)
		lastd = NestedDict.make_path(d,path[:-1])
		lastd[path[-1]]=value
		return

	@staticmethod
	def iter_items(d,prefix=tuple()):
		for k,v in d.items():
			if isinstance(k,str):
				k = prefix + (k,)
			if isinstance(v,dict):
				for k1,v1 in NestedDict.iter_items(v,prefix=k):
					yield k1,v1
			else:
				yield k,v

	@staticmethod
	def compose(*dicts):
		outd = dict()
		for d in dicts:
			for k,v in d.items():
				NestedDict.set(outd,k,v)
		return outd

	@staticmethod
	def simplify(d):
		return {NestedDict.convert_to_pathstring(k):v for k,v in NestedDict.iter_items(d)}


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
		L = dict(csv.reader(s.splitlines(), delimiter=DELIMITER, quoting = csv.QUOTE_NONNUMERIC))
		return NestedDict.compose(L)

	@staticmethod
	def write(d):
		rows = NestedDict.simplify(d).items()
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
	def build_one_line(model,headers,values):
		return {f'{model}.{param}':value for param,value in zip(headers,values) if value != ''}

	@staticmethod
	def read(s):
		elems = list(csv.reader(s.splitlines(), delimiter=DELIMITER,  quoting = csv.QUOTE_NONNUMERIC))
		headers = elems.pop(0)[1:]
		dicts = [CSVUtil.build_one_line(elem[0],headers,elem[1:]) for elem in elems]
		return NestedDict.compose(*dicts)

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



