from obj_model import core
from obj_model import bio
from functools import wraps

# scalar attributes
class IdAttribute(core.StringAttribute):
    def __init__(self):
        super().__init__(default=None,unique=True,primary=True)

class BooleanAttribute(core.BooleanAttribute):
    def __init__(self):
        super().__init__(default=None)

class FloatAttribute(core.FloatAttribute):
    def __init__(self):
        super().__init__(default=None)

class IntegerAttribute(core.IntegerAttribute):
    def __init__(self):
        super().__init__(default=None)

class PositiveIntegerAttribute(core.PositiveIntegerAttribute):
    def __init__(self):
        super().__init__(default=None)

class StringAttribute(core.StringAttribute):
    def __init__(self):
        super().__init__(default=None)

class LongStringAttribute(core.LongStringAttribute):
    def __init__(self):
        super().__init__(default=None)

class RegexAttribute(core.RegexAttribute):
    def __init__(self):
        super().__init__(default=None)


# related attributes
class OneToOneAttribute(core.OneToOneAttribute):pass
class ManyToOneAttribute(core.ManyToOneAttribute):pass
class OneToManyAttribute(core.OneToManyAttribute):pass
class ManyToManyAttribute(core.ManyToManyAttribute):pass

# extra_attributes
class BioSeqAttribute(bio.BioSeqAttribute):
    def __init__(self):
        super().__init__(default=None)

# wrapper for methods that can be called for setting pattern constraints & during simulation
def localfn(fn):
    ''' 
    Takes a function defined with keywords {kw1,kw2...}
    * Makes it an instance function with the same keywords
    * Looks at kwargs specified and sees if keywords are missing
    * Tries to fill in missing kwargs from self's literal attributes. 
    * Ignores other missing kwargs
    * Attaches keyword information and _is_localfn boolean to method attributes.
    '''

    fn._kws = fn.__code__.co_varnames
    fn._is_localfn = True

    @wraps(fn)
    def fn2(self,**kwargs):
        available_attrs = [x for x in self.get_literal_attrs().keys() if x!='id' and getattr(self,x,None) is not None]
        to_fill = [x for x in fn._kws if x not in kwargs and x in available_attrs]
        new_kwargs = {x:getattr(self,x) for x in to_fill}
        return fn(**new_kwargs,**kwargs)
        
    return fn2
