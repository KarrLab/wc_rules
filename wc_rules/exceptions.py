"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-05-25
:Copyright: 2017, Karr Lab
:License: MIT
"""

import wc_rules.mol_schema


class Error(Exception):
    """ Base error class """

    def __init__(self, msg):
        """
        Args:
            msg (:obj:`str`): error message
        """
        super(Error, self).__init__(msg)


class AddObjectError(Error):
    """ Add object error """

    def __init__(self, parent, object, allowed_object_types, method_name='add'):
        """
        Args:
            parent (:obj:`mol_schema.BaseClass`): the parent object to which :obj:`object` cannot be added
            object (:obj:`mol_schema.BaseClass`): the object that cannot be added to :obj:`parent`
            allowed_object_types (:obj:`list` of :obj:`type`): list of types of objects which can be added 
                to :obj:`parent`
            method_name (:obj:`str`, optional): name of the method which generated the error
        """
        msg = ('Objects of type "{}" cannot be added to objects of type "{}" using method "{}". '
               'Only objects of types {{{}}} can be added using this method.').format(
            object.__class__.__name__,
            parent.__class__.__name__,
            method_name,
            ', '.join([t.__name__ for t in allowed_object_types]))
        super(AddObjectError, self).__init__(msg)


class RemoveObjectError(Error):
    """ Remove object error """

    def __init__(self, parent, object, allowed_object_types, method_name='remove', not_found=False):
        """
        Args:
            parent (:obj:`mol_schema.BaseClass`): the parent object to which :obj:`object` cannot be added
            object (:obj:`mol_schema.BaseClass`): the object that cannot be added to :obj:`parent`
            allowed_object_types (:obj:`list` of :obj:`type`): list of types of objects which can be added 
                to :obj:`parent`
            method_name (:obj:`str`, optional): name of the method which generated the error
            not_found (:obj:`bool`, optional):
        """
        if not_found:
            msg = 'Object of type "{}" not found on object of type "{}"'.format(
                object.__class__.__name__,
                parent.__class__.__name__)
        else:
            msg = ('Objects of type "{}" cannot be removed from objects of type "{}" using method "{}". '
                   'Only objects of types {{{}}} can be removed using this method.').format(
                object.__class__.__name__,
                parent.__class__.__name__,
                method_name,
                ', '.join([t.__name__ for t in allowed_object_types]))
        super(RemoveObjectError, self).__init__(msg)
