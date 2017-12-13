"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
from wc_rules import base
from wc_rules import filter


class StateVariable(base.BaseClass):
    value = core.LiteralAttribute()
    filters = core.OneToManyAttribute(filter.Filter, related_name='var')

    def __init__(self, value=None):
        super(StateVariable, self).__init__(value=value)

    def set_value(self, value):
        self.value = value
        return self

    #### used in graph-matching ####
    def compare_values(self, value):
        if self.value is not None:
            return self.value == value
        if len(self.filters) > 0:
            return all(x.does_it_match(value) for x in self.filters)
        return True


class BooleanVariable(StateVariable):
    value = core.BooleanAttribute()

    def set_true(self):
        """ Set value to :obj:`True` """
        self.value = True

    def set_false(self):
        """ Set value to :obj:`False` """
        self.value = False


class NumericVariable(StateVariable):
    value = core.NumericAttribute()


class IntegerVariable(NumericVariable):
    value = core.IntegerAttribute()


class FloatVariable(NumericVariable):
    value = core.FloatAttribute()
