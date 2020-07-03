from .expr_new import process_constraint_string, serialize
from .dependency import DependencyCollector
from .utils import subdict
import math,builtins
from pprint import pformat
from collections import ChainMap
from operator import xor

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
	__builtins__ = None,
	# arithmetic single input
    abs = math.fabs,
    ceil = math.ceil,
    floor = math.floor,
    factorial = math.factorial,
    exp = math.exp,
    expm1 = math.expm1,
    log1p = math.log1p,
    log2 = math.log2,
    log10 = math.log10,
    sqrt = math.sqrt,
    
    # arithmetic double input
    mod = lambda x,y: x % y,
    div = lambda x,y: x // y,
    log = math.log,
    pow = math.pow,

    # trigonometric single input
    acos = math.acos,
    asin = math.asin,
    atan = math.atan,
    atan2 = math.atan2,
    cos = math.cos,
    hypot = math.hypot,
    sin = math.sin,
    tan = math.tan,
	degrees = math.degrees,
    radians = math.radians,
    # famous constants
    pi = lambda : math.pi,
    tau = lambda : math.tau,
    avo = lambda : 6.02214076e23,
    
    # operations on lists
    max = builtins.max,
    min = builtins.min,
    sum = unpacked(math.fsum),
	len = lambda x: x.__len__() if isinstance(x,list) else int(x is not None),
    
    # operations on booleans
    any = unpacked(builtins.any),
    all = unpacked(builtins.all),
    only_one_true = lambda *x: x.count(True)==1,
    only_one_false = lambda *x: x.count(False)==1,
    inv = lambda x: not x,
    
)

class Constraint:
	def __init__(self,keywords,builtins,fn,code,deps):
		self.keywords = keywords
		self.builtins = builtins
		self.fn = fn
		self.code = code
		self.deps = deps

	def to_string(self):
		return pformat(dict(
			keywords = self.keywords,
			builtins = self.builtins,
			code = self.code,
			fn = self.fn
			))

	@classmethod
	def initialize(cls,s):
		tree, depdict = process_constraint_string(s)
		deps, code = DependencyCollector(depdict),serialize(tree)

		keywords = list(deps.variables)
		builtins = subdict(global_builtins, ['__builtins__'] + list(deps.builtins)) 
		
		code2 = 'lambda {vars}: {code}'.format(vars=','.join(keywords),code=code)
		
		try:
			fn = eval(code2,builtins,{})
		except:
			err = "'{code}' does not generate a valid constraint function.".format(code=code)
			raise ValueError(err)
			
		return Constraint(keywords,builtins,fn,code,deps), deps.declared_variable


	@classmethod
	def initialize_strings(cls,strs,cmax=0):
		constraints = dict()
		for s in strs:
			c,var = cls.initialize(s)
			if var is None:
				var = '_'+str(cmax)
				cmax += 1
			constraints[var]= c
		return constraints
		
	def exec(self,match,helpers={}):
		# match is a dict that is equivalent to a pattern match
		d = ChainMap(match,helpers)
		kwargs = subdict(d,self.keywords)
		v = self.fn(**kwargs)
		return v
