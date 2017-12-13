"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core


class Parameter(core.Model):
    symbol = core.StringAttribute(primary=True)
    value = core.FloatAttribute()


class RateExpression(core.Model):
    id = core.StringAttribute(primary=True)
    expr = core.StringAttribute()
    parameters = core.ManyToManyAttribute(Parameter, related_name='expressions')


def main():
    return

if __name__ == '__main__':
    main()
