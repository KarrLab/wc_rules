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
def dynamic(fn):
    fnvars = fn.__code__.co_varnames
    @wraps(fn)
    def outer(self_obj,**kwargs):
        populate_this = [x for x in fnvars if x in self_obj.get_literal_attrs() and x not in kwargs]
        for var in populate_this:
            kwargs[var] = getattr(self_obj,var)
        return fn(**kwargs)
    outer._isdynamic = True
    outer._args = fnvars
    return outer
