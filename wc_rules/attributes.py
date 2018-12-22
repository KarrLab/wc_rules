from obj_model import core
from obj_model import bio

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
