import math,builtins


allowed_builtins = '''
abs ceil factorial floor exp expm1
log log1p log2 log10 pow sqrt
acos asin atan atan2
cos hypot sin tan
pi tau avo
degrees radians
sum any all inv max min
'''.split()

symmetric_functions = '''
sum any all max min
'''
def unpacked(fn):
	''' fn that takes list --> fn that takes *args'''
	return lambda *x: fn(x)

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
    pi = math.pi,
    tau = math.tau,
    avo = 6.02214076e23,
    degrees = math.degrees,
    radians = math.radians,
    max = builtins.max,
    min = builtins.min,
    sum = unpacked(math.fsum),
    any = unpacked(builtins.any),
    all = unpacked(builtins.all),
    inv = lambda x: not x
)



class Constraint:
	def __init__(keywords,builtins,assignment,fn,code):
		self.keywords = keywords
		self.builtins = builtins
		self.assignment = assignment
		self.fn = fn
		self.code = code

	def initialize(code,keywords,builtins=None,assignment=None):
		builtins_dict = dict(__builtins__=None)
		if builtins is not None:
			builtins_dict.update({i:global_builtins[i] for i in builtins})
		try:
			fn = eval(code,builtins_dict,{})
		except:
			err = "'{code}' does not generate a valid constraint function.".format(code=code)
			raise ValueError(err)
		return Constraint(keywords,builtins_dict,assignment,fn,code)

	def __call__(self,kwargs):
		v = self.fn(**{kw:kwargs[kw] for kw in self.keywords})
		outbool = False
		if self.assignment is None:
			err = "'{code}' does not return a boolean value.".format(code=self.code)
			assert isinstance(v,bool), err
			outbool = v
		else:
			err = "Variable '{var}' in '{code}' already has a value.".format(var=self.assignment,code=self.code)
			assert self.assignment not in kwargs, err
			kwargs[self.assignment]=v
			outbool = True
		return (outbool,kwargs)