import math,builtins
import scipy.special
from pprint import pformat
from operator import xor
from functools import wraps

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
    if isinstance(x,(tuple,list)):
        return x.__len__()
    return int(x is not None)

ordered_builtins = 'mod div log pow perm comb'.split()

global_builtins = {
	'__builtins__' : None,
	# arithmetic single input
    'abs' : math.fabs,
    'ceil' : math.ceil,
    'floor' : math.floor,
    'factorial' : math.factorial,
    'exp' : math.exp,
    'expm1' : math.expm1,
    'log1p' : math.log1p,
    'log2' : math.log2,
    'log10' : math.log10,
    'sqrt' : math.sqrt,
    
    # arithmetic double input 
    # order matters
    'mod' : lambda x,y: x % y,
    'div' : lambda x,y: x // y,
    'log' : math.log,
    'pow' : math.pow,

    # trigonometric single input
    'acos' : math.acos,
    'asin' : math.asin,
    'atan' : math.atan,
    'atan2' : math.atan2,
    'cos' : math.cos,
    'hypot' : math.hypot,
    'sin' : math.sin,
    'tan' : math.tan,
	'degrees' : math.degrees,
    'radians' : math.radians,
    # famous constants
    'pi' : (lambda : math.pi),
    'tau' : (lambda : math.tau),
    'avo' : (lambda : 6.02214076e23),
    
    # operations on lists
    'max' : builtins.max,
    'min' : builtins.min,
    'sum' : unpacked(math.fsum) ,
	'len' : compute_len ,
    
    # operations on booleans
    'any' : unpacked(builtins.any),
    'all' : unpacked(builtins.all),
    'only_one_true' : lambda *x: x.count(True)==1,
    'only_one_false' : lambda *x: x.count(False)==1,
    'inv' : lambda x: not x,

    # permutations and combinations
    'perm' : scipy.special.perm,
    'comb' : scipy.special.comb,
    
}
