from .utils import generate_id
from .rete_token import new_token,TokenRegister

class ReteNode(object):
    def __init__(self,id=None):
        if id is None:
            id = generate_id()
        self.id = id
        self.predecessors = set()
        self.successors = set()

    # Rules for token-passing.
    # On receiving a token, do NOT modify it.
    # Use process_token to generate NEW tokens. Old token dies here.
    # Send each new token to each successor (nobody modifies it!)

    def receive_token(self,token,sender,verbose=False):
        # logic for receiving tokens
        # subsequent calls to process_token and send_token
        tokens = self.process_token(token,sender,verbose)
        for token in tokens:
            self.send_token(token,verbose)
        return

    def send_token(self,token,verbose=False):
        # logic for sending token to successors
        for node in self.successors:
            node.receive_token(token,self,verbose)
        return

    # re-implement this method for all subclasses
    def process_token(self,token,sender,verbose=False):
        # logic for processing token internally
        # should generate a list of NEW tokens
        # the old token should be destroyed when this method closes
        tokens_to_pass = [new_token(token)]
        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass))
        return tokens_to_pass

    # messages for verbose mode
    def processing_message(self,token):
        selfstr = '\"' + str(self) + '\"'
        return " ".join([selfstr,'processing',str(token._dict)])

    def passing_message(self,token=None,tab=4):
        tabsp = " "*tab
        if token is None:
            return " ".join([tabsp,'token stops here!'])
        return " ".join([tabsp,'passing',str(token._dict)])

    def adding_message(self,token,tab=4):
        tabsp = " "*tab
        return " ".join([tabsp,'adding',str(token._dict)])

    def removing_message(self,token,tab=4):
        tabsp = " "*tab
        return " ".join([tabsp,'removing',str(token._dict)])

    def verbose_mode_message(self,token,tokens_to_pass=[],tokens_to_add=[],tokens_to_remove=[]):
        strs_processing = [self.processing_message(token)]
        strs_adding = []
        strs_removing = []
        strs_passing = []
        if len(tokens_to_add)>0:
            strs_adding = [self.adding_message(x) for x in tokens_to_add]
        if len(tokens_to_remove)>0:
            strs_removing = [self.removing_message(x) for x in tokens_to_remove]
        if len(tokens_to_pass)>0:
            strs_passing = [self.passing_message(x) for x in tokens_to_pass]
        else:
            strs_passing = [self.passing_message()]
        return '\n'.join(strs_processing + strs_adding + strs_removing + strs_passing)

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

    def process_token(self,token,sender,verbose):
        tokens_to_pass = [new_token(token)]
        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass))
        return tokens_to_pass


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

    def process_token(self,token,sender,verbose):
        tokens_to_pass = [new_token(token)]
        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass))
        return tokens_to_pass

class alias(SingleInputNode):
    def __init__(self,var_tuple,id=None):
        super().__init__(id)
        self.variable_names = var_tuple

    def __str__(self):
        return ','.join(list(self.variable_names))

    def process_token(self,token,sender,verbose):
        tokens_to_pass = [new_token(token)]
        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass))
        return tokens_to_pass

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
