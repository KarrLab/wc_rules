"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

import obj_model.core


class Parameter(obj_model.core.Model):
    """ Represents a parameter 

    Attributes:
        symbol (:obj:`str`): symbol
        value (:obj:`float`): value

        rate_expressions (:obj:`list` of :obj:`RateExpression`): list of rate expressions
    """
    symbol = obj_model.core.StringAttribute(primary=True)
    value = obj_model.core.FloatAttribute()


class RateExpression(obj_model.core.Model):
    """ Represents a rate expression

    Attributes:
        id (:obj:`str`): identifier
        expression (:obj:`str`): expression
        parameters (:obj:`list` of :obj:`Parameter`): list of parameters
    """
    id = obj_model.core.StringAttribute(primary=True)
    expression = obj_model.core.StringAttribute()
    parameters = obj_model.core.ManyToManyAttribute(Parameter, related_name='rate_expressions')
