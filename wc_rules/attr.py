from obj_model import core, extra_attributes


class BooleanAttribute(core.BooleanAttribute):pass
class FloatAttribute(core.FloatAttribute):pass
class IntegerAttribute(core.IntegerAttribute):pass
class PositiveIntegerAttribute(core.PositiveIntegerAttribute):pass
class StringAttribute(core.StringAttribute):pass
class LongStringAttribute(core.LongStringAttribute):pass
class RegexAttribute(core.RegexAttribute):pass
class OneToOneAttribute(core.OneToOneAttribute):pass
class ManyToOneAttribute(core.ManyToOneAttribute):pass
class OneToManyAttribute(core.OneToManyAttribute):pass
class ManyToManyAttribute(core.ManyToManyAttribute):pass

class BioSeqAttribute(extra_attributes.BioSeqAttribute):pass
