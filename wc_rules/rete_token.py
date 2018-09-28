from utils import generate_id
import copy

class ReteToken(object):
    def __init__(self,id=None,level=None,sender=None,vardict=None):
        if id is None:
            id = generate_id()
        if level is None:
            level = 0
        self.id = id
        self.level = level
        self.sender = sender
        self.vardict = vardict

    def duplicate(self,sender=None):
        tok = copy.copy(self)
        tok.level += 1
        if sender is not None:
            tok.sender = sender
        return tok
