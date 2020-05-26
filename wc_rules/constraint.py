import math,builtins
from pprint import pformat
from collections import ChainMap



symmetric_functions = '''
sum any all max min
'''

def unpacked(fn):
	''' fn that takes list --> fn that takes *args'''
	return lambda *x: fn(x)

''' All builtins must be of the form fn(*x),
i.e. take an unpacked list as an argument.
'''
def compute_len(x):
	if isinstance(x,list):
		return x.__len__()
	return int(x is not None)


global_builtins = dict(
    abs = math.fabs,
    ceil = math.ceil,
    factorial = math.factorial,
    floor = math.floor,
    exp = math.exp,
    expm1 = math.expm1,
    log = math.log,
    log1p = math.log1p,
    log2 = math.log2,
    log10 = math.log10,
    pow = math.pow,
    sqrt = math.sqrt,
    acos = math.acos,
    asin = math.asin,
    atan = math.atan,
    atan2 = math.atan2,
    cos = math.cos,
    hypot = math.hypot,
    sin = math.sin,
    tan = math.tan,
    pi = lambda : math.pi,
    tau = lambda : math.tau,
    avo = lambda : 6.02214076e23,
    degrees = math.degrees,
    radians = math.radians,
    max = builtins.max,
    min = builtins.min,
    sum = unpacked(math.fsum),
    any = unpacked(builtins.any),
    all = unpacked(builtins.all),
    inv = lambda x: not x,
    len = compute_len
)

class Constraint:
	def __init__(self,keywords,builtins,assignment,fn,code):
		self.keywords = keywords
		self.builtins = builtins
		self.assignment = assignment
		self.fn = fn
		self.code = code

	def to_string(self):
		return pformat(dict(
			keywords = self.keywords,
			builtins = self.builtins,
			assignment = self.assignment,
			code = self.code,
			fn = self.fn
			))

	@classmethod
	def initialize(cls,deps,code):
		keywords = list(deps.variables)
		builtins = {'__builtins__':None}
		builtins.update({i:global_builtins[i] for i in list(deps.builtins)})
		assignment = deps.declared_variable
		code2 = 'lambda {vars}: {code}'.format(vars=','.join(keywords),code=code)
		
		try:
			fn = eval(code2,builtins,{})
		except:
			err = "'{code}' does not generate a valid constraint function.".format(code=code)
			raise ValueError(err)
		return Constraint(keywords,builtins,assignment,fn,code)

	def process(self,match,builtins=global_builtins,helpers={}):
		# match is a dict that is equivalent to a pattern match
		d = ChainMap(match,builtins,helpers)
		kwargs = {x:d[x] for x in self.keywords}
		v = self.fn(**kwargs)
		if self.assignment is None:
			return v,match
		match.update({self.assignment:v})
		return True,match
