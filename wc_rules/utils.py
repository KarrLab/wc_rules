"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

###### Factory ######
class Factory(object):
    """ Class/instance factory """

    def build(self, cls, names, create_instances=True):
        """ Create a list of new classes with names :obj:`names` that inherit from :obj:`cls`,
        and optionally either return the list of classes or create instances of the new
        classes and return a list of these instances.

        Args:
            cls (:obj:`type`): superclass for the new classes
            names (:obj:`list` of :obj:`str`): names of the new classes
            create_instances (:obj:`bool`, optional): if :obj:`True`, create instances of the
                new classes and return a list of those new instances

        Returns:
            :obj:`list` of :obj:`type` or :obj:`cls`: list of the new classes or a list of
                the instances of the new classes
        """
        new_types_or_instances = []
        for name in names:
            new_type = type(name, (cls,), {})
            if create_instances:
                new_types_or_instances.append(new_type())
            else:
                new_types_or_instances.append(new_type)

        return new_types_or_instances


###### Methods ######
def listify(value):
    """ If :obj:`value` is list, return :obj:`value`. Otherwise, return a list
    that contains the element :obj:`value`.

    Args:
        value (:obj:`object`): value

    Returns:
        :obj:`list`: If :obj:`value` is list, return :obj:`value`. Otherwise,
            return a list that contains the element :obj:`value`.
    """
    if isinstance(value, list):
        return value
    return [value]
