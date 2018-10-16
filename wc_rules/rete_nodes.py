from .utils import generate_id
from .rete_token import Token,TokenRegister

class ReteNode(object):
    def __init__(self,id=None):
        if id is None:
            id = generate_id()
        self.id = id
        self.predecessors = set()
        self.successors = set()

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
        # should generate a list of tokens
        if verbose:
            print(self.processing_message(token))
        return [token]

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

    def verbose_mode_message(self,token,passthru_tokens,added_tokens=None):
        str1 = self.processing_message(token)
        strs_added = []
        strs_passthru = []
        if added_tokens:
            strs_added = [self.adding_message(x) for x in added_tokens]
        if len(passthru_tokens)==0:
            strs_passthru = [self.passing_message()]
        else:
            strs_passthru = [self.passing_message(x) for x in passthru_tokens]
        return '\n'.join([str1] + strs_added + strs_passthru)


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
        passthru_tokens = []
        if 'node' in token.keys():
            if isinstance(token['node'],self._class):
                passthru_tokens = [token]
        if verbose:
            print(self.verbose_mode_message(token,passthru_tokens))
        return passthru_tokens

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
        added_tokens = []
        passthru_tokens = []
        if 'node' in token.keys():
            d = {'node':token['node']}
            if self._register.get(d) is None:
                t = Token(d)
                self._register.add_token(t)
                added_tokens = [t]
                passthru_tokens = [t.duplicate()]
        if verbose:
            print(self.verbose_mode_message(token,passthru_tokens,added_tokens))
        return passthru_tokens

class alias(SingleInputNode):
    def __init__(self,var_tuple,id=None):
        super().__init__(id)
        self.variable_names = var_tuple

    def __str__(self):
        return ','.join(list(self.variable_names))

    def process_token(self,token,sender,verbose):
        passthru_tokens = []
        if 'node' in token.keys():
            keymap = {'node':self.variable_names[0]}
            d = {keymap['node']:token['node']}
            passthru_tokens = [Token(d)]
        else:
            # this is for alias Pattern nodes
            # may need fixing later
            passthru_tokens = [token]
        if verbose:
            print(self.verbose_mode_message(token,passthru_tokens))
        return passthru_tokens

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
