from .expr import process_expression_string, serialize
from .dependency import DependencyCollector
from .utils import subdict
import math,builtins
import scipy.special
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

ordered_builtins = 'mod div log pow perm comb'.split()

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

    # permutations and combinations
    perm = scipy.special.perm,
    comb = scipy.special.comb,
    
)

class ExecutableExpression:
	# is a fancy lambda function that can be executed
	start = None
	builtins = {}

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
		try:
			tree, depdict = process_expression_string(s,start=cls.start)
			deps, code = DependencyCollector(depdict),serialize(tree)
			#if deps.has_subvariables:
			#	err = 'Code `{s}` is nesting too many variables'
			#	assert has_subvariables, err.format(s=s) 
			keywords = list(deps.variables)
			builtins = subdict(cls.builtins, ['__builtins__'] + list(deps.builtins))
			code2 = 'lambda {vars}: {code}'.format(vars=','.join(keywords),code=code)
			try:
				fn = eval(code2,builtins,{})
				x = cls(keywords=keywords,builtins=builtins,fn=fn,code=code,deps=deps)
			except:
				x = None
		except:
			x = None
		# Note checking of valid object is OUTSIDE the control of this factory method
		return x

	@classmethod
	def initialize_from_strings(cls,strings,classes,cmax=0):
		d = dict()
		allowed_forms = '\n'.join([x for c in classes for x in c.allowed_forms])
		for s in strings:
			for c in classes:
				x = c.initialize(s)
				if x is not None:
					break
			if x is None:
				err = "`{s}` does not create a valid instance of {c}. It must have one of the forms:\n {f}"
				raise ValueError(err.format(s=s,c=classes,f=allowed_forms))

			if x.deps.declared_variable is not None:
				d[x.deps.declared_variable] = x
			else:
				d['_{0}'.format(cmax)] = x
				cmax += 1
		return d

	def exec(self,*dicts):
		d = ChainMap(*dicts)
		kwargs = {x:d[x] for x in self.keywords}
		v = self.fn(**kwargs)
		if self.__class__.allowed_returns is not None:
			types = self.__class__.allowed_returns
			err = 'Value {v} returned by {cls} `{code}` is not one of {types}.'
			assert isinstance(v,types), err.format(v=v,code=self.code,cls=self.__class__.__name__,types=types)
		return v
		

class Constraint(ExecutableExpression):
	start = 'boolean_expression'
	builtins = global_builtins
	allowed_forms = ['<expr> <bool_op> <expr>']
	allowed_returns = (bool,)
			
class Computation(ExecutableExpression):
	start = 'assignment'
	builtins = global_builtins
	allowed_forms = ['<var> = <expr>']
	allowed_returns = None

class RateLaw(ExecutableExpression):
	start = 'expression'
	builtins = global_builtins
	allowed_forms = ['<expr>']
	allowed_returns = (int,float,)


def initialize_from_string(string,classes):
	for c in classes:
		x = c.initialize(string)
		if x is not None:
			return x
	err = 'Could not create a valid instance of {0} from {1}'
	assert False, err.format(classes,string)
	