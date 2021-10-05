from .parse import process_expression_string, serialize
from .dependency import DependencyCollector
from ..utils.collections import subdict
from ..schema.actions import RollbackAction, TerminateAction
from .builtins import ordered_builtins, global_builtins
from .exprgraph import dfs_make
from collections import ChainMap

def register_builtin(name,fn,ordered_arguments=True):
	global ordered_builtins
	global global_builtins

	global_builtins[name] = fn
	if ordered_arguments:
		ordered_builtins.append(name)
	return

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

			# this step figures what builtins to use, picks them from the global_builtins list
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

	def build_exprgraph(self):
		tree, deps = process_expression_string(self.code,start=self.__class__.start)
		return dfs_make(tree)

	def full_string(self):
		return self.code	

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

	def build_exprgraph(self):
		assert self.deps.declared_variable is not None
		code = f'{self.deps.declared_variable} = {self.code}'
		tree, deps = process_expression_string(code,start=self.__class__.start)
		return dfs_make(tree)

	def full_string(self):
		return f'{self.deps.declared_variable} = {self.code}'


class RateLaw(ExecutableExpression):
	start = 'expression'
	builtins = global_builtins
	allowed_forms = ['<expr>']
	allowed_returns = (int,float,)

######## Simulator methods #########
def rollback(expr):
    assert isinstance(expr,bool), "Rollback condition must evaluate to a boolean."
    return {True:RollbackAction(),False:[]}[expr]
setattr(rollback,'_is_action',True)

def terminate(expr):
    assert isinstance(expr,bool), "Terminate condition must evaluate to a boolean."
    return {True:TerminateAction(),False:[]}[expr]
setattr(terminate,'_is_action',True)

########### ActionCaller ##########
# an executable expression object that when called on a match
# is equivalent to an action method call
class ActionCaller(ExecutableExpression):
    start = 'function_call'
    builtins = ChainMap(global_builtins,dict(rollback=rollback,terminate=terminate))
    allowed_forms = ['<actioncall> ( <boolexpr> )', '<pattern>.<var>.<actioncall> (<params>)', '<pattern>.<actioncall> (<params>)']

    def exec(self,matches,helpers):
        v = super().exec(matches,helper)
        #err = 'An element in the following nested list is not a recognized Action: {0}'
        #assert verify_list(v,(SimulatorAction,PrimaryAction,CompositeAction)), err.format(list(v))
        # verifying that every element of a nested list is an action is slow AF
        # just don't do any verification here
        # todo: verification can be done by the simulator when it processes the output of an action caller.
        return v  

def initialize_from_string(string,classes):
	for c in classes:
		x = c.initialize(string)
		if x is not None:
			return x
	err = 'Could not create a valid instance of {0} from {1}'
	assert False, err.format(classes,string)
