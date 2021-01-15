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

ordered_builtins = 'mod div log pow'.split()

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
    # order matters
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

class LambdaObject:
	# is a fancy lambda function that can be executed

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
	def process(cls,s,start,builtins):
		tree, depdict = process_constraint_string(s,start=start)
		deps, code = DependencyCollector(depdict),serialize(tree)
		keywords = list(deps.variables)
		builtins = subdict(builtins, ['__builtins__'] + list(deps.builtins))
		code2 = 'lambda {vars}: {code}'.format(vars=','.join(keywords),code=code)
		try:
			fn = eval(code2,builtins,{})
		except:
			err = "'{code}' does not generate a execution object.".format(code=code)
			raise ValueError(err)

		return dict(keywords=keywords,builtins=builtins,fn=fn,code=code,deps=deps)


class Constraint(LambdaObject):
	builtins = global_builtins
	
	@classmethod
	def initialize(cls,s,has_subvariables=False):
		# has_subvariables behavior
		# for patterns, the node variable is the top level, e.g. a.x, a.f(), etc.
		# for rules, the pattern variable is the top level, e.g., p.a.x, p.a.f(), etc.
		# Constraint objects are common to both patterns and rules
		# but only rules can have subvariables (see grammar in expr_new.py)
		creation_params = LambdaObject.process(s,start='start',builtins=cls.builtins)
		deps,code = [creation_params.get(x,None) for x in ['deps','code']]

		if deps.has_subvariables and not has_subvariables:
			err = "Nested variables disallowed in '{code}'".format(code=code)
			raise ValueError(err)

		return cls(**creation_params), deps.declared_variable
			
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
