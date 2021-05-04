from copy import deepcopy
import json, csv, io
import yaml

from pathlib import Path
from collections import defaultdict

DELIMITER = ','

def flatten_dict(d):
	if not isinstance(d,dict):
		return d
	outd = dict()
	for k,v in d.items():
		v = flatten_dict(v)
		if isinstance(v,dict):
			for k1,v1 in v.items():
				outd[(k,*k1)] = v1
		else:
			outd[(k,)] = v
	return outd

def unflatten_dict(d):
	outd = dict()
	for k, v in d.items():
		priors, final = k[:-1], k[-1]
		refd = outd
		for k1 in priors:
			if (k1 in refd and not isinstance(refd[k1],dict)) or (k1 not in refd):
				refd[k1] = dict()
			refd = refd[k1]
		refd[final] = v
	return outd


def join_dicts(*dicts):
	# only one level of nesting
	return {k:v for d in dicts for k,v in d.items()}

def ordered_unique_elems(L):
	outL = list()
	outS = set()
	for elem in L:
		if elem not in outS:
			outL.append(elem)
			outS.add(elem)
	return outL

def compose_data(*dicts):
	return unflatten_dict(join_dicts(*[flatten_dict(d) for d in dicts]))


class YAMLUtil:
	@staticmethod
	def read(s):
		return yaml.load(s)

	@staticmethod
	def write(d):
		return yaml.dump(d,default_flow_style=False)

class JSONUtil:

	@staticmethod
	def read(s):
		return json.loads(s)

	@staticmethod
	def write(d):
		return json.dumps(d,indent=4)

class PLISTUtil:

	@staticmethod
	def read(s):
		d1 = list(csv.reader(s.splitlines(),delimiter=DELIMITER,  quoting = csv.QUOTE_NONNUMERIC))
		d2 = {tuple(x.split('.')):y for x,y in d1}
		return unflatten_dict(d2)


	@staticmethod
	def write(d):
		rows = [['.'.join(k),v] for k,v in flatten_dict(d).items()]
		s = io.StringIO()
		w = csv.writer(s,delimiter=DELIMITER, quoting = csv.QUOTE_NONNUMERIC)
		w.writerows(rows)
		return s.getvalue()

class CSVUtil:

	@staticmethod
	def read(s):
		# uses first row as header
		elems = list(csv.reader(s.splitlines(),delimiter=DELIMITER,  quoting = csv.QUOTE_NONNUMERIC))
		headers = elems.pop(0)[1:]
		d = dict()
		for elem in elems:
			model = elem[0].split('.')
			for p,v in zip(headers,elem[1:]):
				d[tuple(model + [p])] = v
		return unflatten_dict(d)

	@staticmethod
	def write(d):
		elems = flatten_dict(d)
		fieldnames = ['model'] + ordered_unique_elems(k[-1] for k in elems)
		d1 = defaultdict(dict)
		for k, v in elems.items():
			d1['.'.join(k[:-1])][k[-1]] = v
		rows = [join_dicts({'model':mname},mparams) for mname, mparams in d1.items()]
		
		s = io.StringIO()
		w = csv.DictWriter(s,delimiter=DELIMITER, fieldnames = fieldnames, quoting = csv.QUOTE_NONNUMERIC)
		w.writeheader() 
		w.writerows(rows)
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

	def read_file(self,filename,data_format=None):
		file = self.folder / filename
		if data_format is None:
			data_format = file.suffix[1:]
		txt = file.read_text()
		data = self.utils[data_format].read(txt)
		return data
		
	def write_file(self,data,filename,data_format=None):
		file = self.folder / filename
		if data_format is None:
			data_format = file.suffix[1:]
		txt = self.utils[data_format].write(data)
		if not self.folder.exists():
			self.folder.mkdir(parents=True)
		file.write_text(txt)
		return
	
	def read_files(self,filenames=[]):
		if filenames == []:
			files = sorted(self.folder.glob('*.*'))
		else:
			files = [self.folder / x for x in filenames]
		return {file.stem:self.read_file(file.name) for file in files}



