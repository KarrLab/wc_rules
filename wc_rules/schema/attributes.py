from obj_tables import core
from obj_tables.bio import seq
from functools import wraps,partial

def check_numeric_value(value,attr,_class,_min=None,_max=None):
    if value is None:
        return
    err = "Attribute `{attr}` takes value None or any value of class `{_class}`."
    assert isinstance(value,_class), err.format(attr=attr,_class=_class.__name__)
    err = "Attribute `{attr}` takes value of class `{_class}` in the range [{_min},{_max}]."
    if _min is not None:
        assert value >= _min, err.format(attr=attr,_class=_class.__name__,_min=_min,_max=_max)
    if _max is not None:
        assert value <= _max, err.format(attr=attr,_class=_class.__name__,_min=_min,_max=_max)
    return 

def check_string_value(value,attr):
    if value is None:
        return
    err = "Attribute `{attr}` can take value None or any value of class `{_class}`."
    assert isinstance(value,str), err.format(attr=attr,_class=str.__name__)

# scalar attributes
class IdAttribute(core.StringAttribute):
    def __init__(self):
        super().__init__(default=None,unique=True,primary=True)

    def check_value(self,value):
        return check_string_value(value,self.name)

class BooleanAttribute(core.BooleanAttribute):
    
    def __init__(self):
        super().__init__(default=None)

    def check_value(self,value):
        return check_numeric_value(attr=self.name,value=value,_class=bool)

class FloatAttribute(core.FloatAttribute):
    
    def __init__(self):
        super().__init__(default=None)
    #TODO: float attribute min max not setting properly

class IntegerAttribute(core.IntegerAttribute):
    
    def __init__(self,min=None,max=None,):
        super().__init__(default=None,min=min,max=max)

    def check_value(self,value):
        return check_numeric_value(attr=self.name,value=value,_class=int,_min=self.min,_max=self.max)

class PositiveIntegerAttribute(core.PositiveIntegerAttribute):

    def __init__(self,max=None):
        super().__init__(default=None,max=max)

    def check_value(self,value):
        return check_numeric_value(attr=self.name,value=value,_class=int,_min=0,_max=self.max)

class StringAttribute(core.StringAttribute):
    def __init__(self):
        super().__init__(default=None)

    def check_value(self,value):
        return check_string_value(value,self.name)

class LongStringAttribute(core.LongStringAttribute):
    def __init__(self):
        super().__init__(default=None)

class RegexAttribute(core.RegexAttribute):
    def __init__(self):
        super().__init__(default=None)

# related attributes
class OneToOneAttribute(core.OneToOneAttribute):
    pass
        
class ManyToOneAttribute(core.ManyToOneAttribute):
    pass

class OneToManyAttribute(core.OneToManyAttribute):
    pass

class ManyToManyAttribute(core.ManyToManyAttribute):
    pass

# extra_attributes
class BioSeqAttribute(seq.SeqAttribute):
    def __init__(self):
        super().__init__(default=None)

    def check_value(self,value):
        return isinstance(value,str)

# wrapper for methods that can be called for setting pattern constraints & during simulation
def computation(fn):
    ''' 
    Takes a function defined with keywords {kw1,kw2...}
    * Makes it an instance function with the same keywords
    * Looks at kwargs specified and sees if keywords are missing
    * Tries to fill in missing kwargs from self's literal attributes. 
    * Ignores other missing kwargs
    * Attaches keyword information and _is_localfn boolean to method attributes.
    '''

    fn._kws = fn.__code__.co_varnames
    fn._is_computation = True

    @wraps(fn)
    def fn2(self,**kwargs):
        available_attrs = [x for x in self.get_literal_attrs().keys() if x!='id' and getattr(self,x,None) is not None]
        to_fill = [x for x in fn._kws if x not in kwargs and x in available_attrs]
        new_kwargs = {x:getattr(self,x) for x in to_fill}
        return fn(**new_kwargs,**kwargs)
        
    return fn2

# wrapper for methods that implement actions in a rule
def action(fn):
    fn._is_action = True
    return fn
