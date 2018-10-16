from .utils import generate_id
from .rete_token import Token,TokenRegister

class ReteNode(object):
    def __init__(self,id=None):
        if id is None:
            id = generate_id()
        self.id = id
        self.predecessors = set()
        self.successors = set()

    def receive_token(self,token,sender):
        # logic for receiving tokens
        # subsequent calls to process_token and send_token
        tokens = self.process_token(token)
        for token in tokens:
            self.send_token(token)
        return

    def send_token(self,token):
        # logic for sending token to successors
        for node in self.successors:
            node.receive_token(token,self)
        return

    def process_token(self,token):
        # logic for processing token internally
        # should generate a list of tokens
        selfstr = str(self).replace("\n",",")
        print( " "*token.level + selfstr)
        tok = token.duplicate(sender=self.id)
        return [tok]


class SingleInputNode(ReteNode): pass

class Root(SingleInputNode):
    def __init__(self):
        super().__init__(id='root')

    def __str__(self):
        return 'root'

class check(SingleInputNode):
    def __init__(self,id=None):
        super().__init__(id)

class checkTYPE(check):
    def __init__(self,_class,id=None):
        super().__init__(id)
        self._class = _class

    def __str__(self):
        return 'isinstance(*,'+self._class.__name__+')'

class checkATTR(check):
    operator_dict = {
    'lt':'<', 'le':'<=',
    'eq':'==', 'ne':'!=',
    'ge':'>=', 'gt':'>',
    }
    def __init__(self,tuple_of_attr_tuples,id=None):
        super().__init__(id)
        self.tuple_of_attr_tuples = tuple_of_attr_tuples

    def __str__(self):
        strs = []
        for tup in self.tuple_of_attr_tuples:
            attrname = tup[0]
            opname = self.operator_dict[tup[1].__name__]
            value = str(tup[2])
            strs.append(''.join(['*.',attrname,opname,value]))
        return '\n'.join(strs)

class store(SingleInputNode):
    def __init__(self,id=None):
        super().__init__(id)
        self._register = TokenRegister()

    def __str__(self):
        return 'store'

class alias(SingleInputNode):
    def __init__(self,var_tuple,id=None):
        super().__init__(id)
        self.variable_names = var_tuple

    def __str__(self):
        return ','.join(list(self.variable_names))

class checkEDGETYPE(check):
    def __init__(self,attrpair,id=None):
        super().__init__(id)
        self.attribute_pair = attrpair

    def __str__(self):
        v = ['*'+str(i)+'.'+x for i,x in enumerate(self.attribute_pair)]
        return '--'.join(v)

class merge(ReteNode):
    def __init__(self,var_tuple,id=None):
        super().__init__(id)
        self.variable_names = var_tuple
        self._register = TokenRegister()

    def __str__(self):
        return ','.join(self.variable_names)
