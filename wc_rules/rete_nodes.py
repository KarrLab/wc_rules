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
        tokens_to_pass = []
        passthrough_fail = ''
        evaluate = self.evaluate_token(token)
        if evaluate:
            tokens_to_pass = [new_token(token)]
        else:
            passthrough_fail = self.passthrough_fail_message()
        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass,passthrough_fail=passthrough_fail))
        return tokens_to_pass

    def evaluate_token(self,token):
        # Here, use the internal variables of self to evaluate whether token
        # should be passed through
        return True

    # messages for verbose mode
    def processing_message(self,token):
        selfstr = '\"' + str(self) + '\"'
        return " ".join([selfstr,'processing',str(token)])

    def failing_message(self,msg='',tab=4):
        tabsp = " "*tab
        msg = '`'+msg+'`'
        return " ".join([tabsp,'passthrough failed! token stops here. Reason:',msg])

    def passing_message(self,token,tab=4):
        tabsp = " "*tab
        return " ".join([tabsp,'passing',str(token)])

    def adding_message(self,token,tab=4):
        tabsp = " "*tab
        return " ".join([tabsp,'adding',str(token)])

    def removing_message(self,token,tab=4):
        tabsp = " "*tab
        return " ".join([tabsp,'removing',str(token)])

    def verbose_mode_message(self,token,tokens_to_pass=[],tokens_to_add=[],tokens_to_remove=[],passthrough_fail=''):
        strs_processing = [self.processing_message(token)]
        strs_adding = []
        strs_removing = []
        strs_passing = []
        strs_fail = []
        if len(tokens_to_add)>0:
            strs_adding = [self.adding_message(x) for x in tokens_to_add]
        if len(tokens_to_remove)>0:
            strs_removing = [self.removing_message(x) for x in tokens_to_remove]
        if passthrough_fail != '':
            strs_fail = [self.failing_message(passthrough_fail)]
        strs_passing = [self.passing_message(x) for x in tokens_to_pass]
        return '\n'.join(strs_processing + strs_adding + strs_removing + strs_fail + strs_passing)


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

    # checkTYPE has PASSTHROUGH functionality.
    # It simply evaluates token, and if it passes,
    # It duplicates it and passes it along
    def evaluate_token(self,token):
        return isinstance(token['node'],self._class)

    def passthrough_fail_message(self):
        return 'Evaluation failed!'

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
    def __init__(self,id=None,number_of_variables=1):
        super().__init__(id)
        self._register = TokenRegister()
        self._number_of_variables = number_of_variables

    def __str__(self):
        return 'store'

    def __len__(self):
        return len(self._register)

    def keys(self):
        if self._number_of_variables==1:
            return ['node']
        if self._number_of_variables==2:
            return ['node1','node2']
        return None

    ### Store does not have passthrough functionality.
    # depending on whether token is Add or Remove
    # they update their register
    # then pass out their updated register tokens

    def process_token(self,token,sender,verbose):
        token_type = token.get_type()
        existing_token = self._register.get(token)
        tokens_to_pass = []
        tokens_to_add = []
        tokens_to_remove = []
        passthrough_fail = ''
        subtoken = token.get_subtoken(self.keys())
        # Add token if existing_token is None and type is 'add'
        if token_type=='add' and existing_token is None:
            tokens_to_add = [new_token(subtoken)]
            tokens_to_pass = [new_token(subtoken)]
        # Remove token if existing_token is not None and type is 'remove'
        elif token_type=='remove' and existing_token is not None:
            tokens_to_remove = [existing_token]
            tokens_to_pass = [new_token(existing_token,invert=True)]
        else:
            # do nothing
            passthrough_fail = self.passthrough_fail_message(token_type)

        # implement changes
        for token in tokens_to_add:
            self._register.add_token(token)
        for token in tokens_to_remove:
            self._register.remove_token(token)

        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass,tokens_to_add,tokens_to_remove,passthrough_fail))
        return tokens_to_pass

    def passthrough_fail_message(self,msgtype='add'):
        if msgtype=='add':
            return 'Token already found in register. Cannot add again!'
        if msgtype=='remove':
            return 'Token not found in register. Cannot remove!'
        return ''

class alias(SingleInputNode):
    def __init__(self,var_tuple,id=None):
        super().__init__(id)
        self.variable_names = var_tuple

    def __str__(self):
        return ','.join(list(self.variable_names))

    def __len__(self):
        return len(list(self.predecessors)[0])

    def transform_token(self,token):
        keymap = {}
        if len(self.variable_names)==1:
            keymap = dict(zip(['node'],self.variable_names))
        if len(self.variable_names)==2:
            keymap = dict(zip(['node1','node2'],self.variable_names))
        return new_token(token,keymap=keymap,subsetkeys=keymap.keys())

    ### alias is PASSTHROUGH with a twist
    # it has to use an internal keymap to transform the incoming token first

    def process_token(self,token,sender,verbose):
        transformed_token = self.transform_token(token)
        return super().process_token(transformed_token,sender,verbose)

    def passthrough_fail_message(self):
        return 'Somthing wrong with aliasing!'

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

    def __len__(self):
        return len(self._register)
