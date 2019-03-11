"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""
import uuid
import random


# Seed for creating ids
# To modify this seed, load utils module, then execute utils.idgen.seed(<new_seed>)
idgen = random.Random()
idgen.seed(0)

###### Methods ######
def iter_to_string(iterable):
    return '\n'.join([str(x) for x in list(iterable)])

def generate_id():
    return str(uuid.UUID(int=idgen.getrandbits(128)))

###### Error ######
class GenericError(Exception):

    def __init__(self, msg=None):
        if msg is None:
            msg = ''
        super(GenericError, self).__init__(msg)

class ReteNetworkError(GenericError):pass

class IndexerError(GenericError):pass
class SlicerError(GenericError):pass

class ValidateError(GenericError):pass

class BuildError(GenericError):
    pass

class AddError(GenericError):
    pass


class RemoveError(GenericError):
    pass


class SetError(GenericError):
    pass


class FindError(GenericError):
    pass

class SeqError(GenericError):
    pass

class ParseExpressionError(GenericError):pass

class AddObjectError(Exception):

    def __init__(self, parentobject, currentobject, allowedobjects, methodname='add()'):
        msg = '\nObject of type ' + self.to_str(currentobject) + ' cannot be added to ' + \
            self.to_str(parentobject) + ' using ' + methodname + '. '
        if (len(allowedobjects) == 1 or isinstance(allowedobjects, str)):
            msg2 = str(allowedobjects)
        else:
            msg2 = ', '.join(allowedobjects)
        msg = msg + 'Only objects of type ' + msg2 + ' are allowed for this method.'
        super(AddObjectError, self).__init__(msg)

    @staticmethod
    def to_str(obj):
        msg = str(type(obj))
        msg = ''.join(filter(lambda ch: ch not in "<>", msg))
        return msg


class RemoveObjectError(Exception):

    def __init__(self, parentobject, currentobject, allowedobjects, methodname='remove()', notfound=False):
        if notfound == False:
            msg = '\nObject of type ' + self.to_str(currentobject) + ' cannot be removed from ' + \
                self.to_str(parentobject) + ' using ' + methodname + '. '
            if (len(allowedobjects) == 1 or isinstance(allowedobjects, str)):
                msg2 = str(allowedobjects)
            else:
                msg2 = ', '.join(allowedobjects)
            msg = msg + 'Only objects of type ' + msg2 + ' are allowed for this method.'
        else:
            msg = '\nObject ' + self.to_str(currentobject) + ' not found!'
        super(AddObjectError, self).__init__(msg)

    @staticmethod
    def to_str(obj):
        msg = str(type(obj))
        msg = ''.join(filter(lambda ch: ch not in "<>", msg))
        return msg
