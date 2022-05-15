from .parse import process_expression_string, serialize
from .dependency import DependencyCollector
from ..utils.collections import subdict
from ..schema.actions import RollbackAction, TerminateAction, PrimaryAction, CompositeAction, SimulatorAction, action_builtins, CollectReferences
from .builtins import ordered_builtins, global_builtins
from .exprgraph import dfs_make
from collections import ChainMap, defaultdict
from sortedcontainers import SortedSet
from frozendict import frozendict
from collections.abc import Sequence

import inspect

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
	builtins = global_builtins

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
				fn = eval(code2,builtins)
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


class ObservableExpression(ExecutableExpression):
	start = 'expression'
	builtins = global_builtins
	allowed_forms = ['<expr>']
	allowed_returns = None

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
	builtins = ChainMap(global_builtins,dict(rollback=rollback,terminate=terminate),action_builtins)
	allowed_forms = ['<actioncall> ( <boolexpr> )', '<pattern>.<var>.<actioncall> (<params>)', '<pattern>.<actioncall> (<params>)']
	allowed_returns = None

	def exec(self,match,*dicts):
		v = super().exec(match,*dicts)
		return v  

def initialize_from_string(string,classes):
	for c in classes:
		x = c.initialize(string)
		if x is not None:
			return x
	err = 'Could not create a valid instance of {0} from {1}'
	assert False, err.format(classes,string)


class ExecutableExpressionManager:
	# assume top-level variable are variables of a pattern
	# e.g., a.x => a is a node on a pattern, x is an attribute
	# similarly, a.x(), x is a computation

	def __init__(self,constraint_execs,namespace):
		self.execs = constraint_execs
		self.namespace = namespace

	def pprint(self):
		return '\n'.join([x.code for x in self.execs])

	def get_attribute_calls(self):
		attrcalls = defaultdict(SortedSet)
		for c in self.execs:
			for k,v in c.deps.attribute_calls.items():
				attrcalls[k].update(v)
			for fnametuple in c.deps.function_calls:
				if len(fnametuple)==2:
					var,fname = fnametuple
					if isinstance(self.namespace[var],type):
						_class = self.namespace[var]
						fn = getattr(_class,fname)
						assert fn._is_computation, f'Could not find function {fnametuple}'
						kws = sorted(set(fn._kws) & set(_class.get_literal_attrs()))
						attrcalls[var].update(kws) 
		for k,v in attrcalls.items():
			for a in v:
				yield k,a

	def get_helper_calls(self):
		helpercalls = defaultdict(SortedSet)
		for c in self.execs:
			for fnametuple,kwargs in c.deps.function_calls.items():
				if len(fnametuple)==2:
					var,fname = fnametuple
					if self.namespace[var]=='Helper Pattern':
						helpercalls[var].add(tuple(kwargs['kwpairs']))
		for k,v in helpercalls.items():
			for tup in v:
				yield k,tup

	def exec(self,match,*dicts):
		for c in self.execs:
			if c.deps.declared_variable is not None:
				match[c.deps.declared_variable] = c.exec(match,*dicts)
			elif not c.exec(match,*dicts):
				return None
		return match


class ActionManager:
	def __init__(self,action_execs,factories):
		self.execs = action_execs

		for e in self.execs:
			for fnametuple in e.deps.function_calls:
				if fnametuple == ('add',):
					assert len(e.deps.variables)==1
					var = list(e.deps.variables)[0]
					assert var in factories
					setattr(e,'build_variable',var)


	def exec(self,match,*dicts):
		for c in self.execs:
			actions = c.exec(match,*dicts)
			if hasattr(c,'build_variable'):
				assert isinstance(actions[-1],CollectReferences)
				actions[-1].variable = c.build_variable
			if isinstance(actions,Sequence):
				yield from actions
			else:
				yield actions

