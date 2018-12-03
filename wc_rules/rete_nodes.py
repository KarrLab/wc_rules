from .utils import generate_id
from .rete_token import new_token,TokenRegister
from sortedcontainers import SortedSet
from operator import attrgetter
from .euler_tour import EulerTour, EulerTourIndex

class ReteNode(object):
    def __init__(self,id=None):
        if id is None:
            id = generate_id()
        self.id = id
        self.predecessors = set()
        self.successors = SortedSet(key=attrgetter('priority'))

    # Rules for token-passing.
    # On receiving a token, do NOT modify it.
    # Use process_token to generate NEW tokens. Old token dies here.
    # Send each new token to each successor (nobody modifies it!)

    def receive_token(self,token,sender,verbose=False):
        # logic for receiving tokens
        # subsequent calls to process_token and send_token
        tokens = []
        if self.entry_check(token):
            tokens = self.process_token(token,sender,verbose)
        for token in tokens:
            self.send_token(token,verbose)
        return

    def send_token(self,token,verbose=False):
        # logic for sending token to successors
        for node in self.successors:
            node.receive_token(token,self,verbose)
        return

    def entry_check(self,token):
        return True

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

    def select_random(self,n=1):
        return []

    def count(self):
        return None

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
        self.priority=4

    def __str__(self):
        return 'isinstance(*,'+self._class.__name__+')'

    # checkTYPE has PASSTHROUGH functionality.
    # It simply evaluates token, and if it passes,
    # It duplicates it and passes it along

    def evaluate_token(self,token):
        return isinstance(token['node'],self._class)

    def passthrough_fail_message(self):
        return 'Evaluation failed! Token node does not match type.'

    def entry_check(self,token):
        return 'node' in token

class checkATTR(check):
    operator_dict = {
    'lt':'<', 'le':'<=',
    'eq':'==', 'ne':'!=',
    'ge':'>=', 'gt':'>',
    }
    def __init__(self,tuple_of_attr_tuples,id=None):
        super().__init__(id)
        self.tuple_of_attr_tuples = tuple_of_attr_tuples
        self.attrs = [tup[0] for tup in tuple_of_attr_tuples]
        self.priority=4
        # tuple of attrtuple is a tuple of (attr,op,value)
        # attr is a string, op is an operator object

    # checkATTR has PASSTHROUGH functionality.
    # However, token passing is a bit more complex than checkTYPE
    # shared attrs <==> token has modified_attrs overlapping with self.attrs

    # Case 0: Token is Remove type. Pass it on.
    # Why? Remove instructions supersede everything else.

    # Case 1: Token is Add type, but no shared attrs. Do nothing.
    # Why? If relevant attrs weren't modified, downstream matches are unaffeced.

    # Case 2: Token is Add type with shared attrs.
    # Evaluate attr expressions. If true, pass it on.
    # Why? New match. Needs to be added.

    # Case 3: Token is Add type with shared attrs.
    # Evaluate attr expressions. If false, invert and pass it on.
    # Why? Potential old match that is currently failing. Need to be deleted if so.

    def process_token(self,token,sender,verbose=False):
        tokens_to_pass = []
        passthrough_fail = ''
        if token.get_type()=='remove':
            tokens_to_pass = [new_token(token)]
        elif not self.has_shared_attrs(token):
            passthrough_fail = self.passthrough_fail_message()
        elif self.evaluate_expressions(token):
            tokens_to_pass = [new_token(token)]
        else:
            tokens_to_pass = [new_token(token,invert=True)]

        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass,passthrough_fail=passthrough_fail))
        return tokens_to_pass

    def __str__(self):
        strs = []
        for tup in self.tuple_of_attr_tuples:
            attrname = tup[0]
            opname = self.operator_dict[tup[1].__name__]
            value = str(tup[2])
            strs.append(''.join(['*.',attrname,opname,value]))
        return '\n'.join(strs)

    def has_shared_attrs(self,token):
        return len([x for x in self.attrs if x in token['modified_attrs']]) > 0

    def evaluate_expression(self,node,attr,op,value):
        return op(getattr(node,attr),value)

    def evaluate_expressions(self,token):
        node = token['node']
        return all([self.evaluate_expression(node,attr,op,value) for attr,op,value in self.tuple_of_attr_tuples])

    def passthrough_fail_message(self):
        return 'Evaluation failed! Token has no shared attributes with node queries.'

    def entry_check(self,token):
        return 'node' in token

class checkEDGE(check):
    def __init__(self,attrpair,id=None):
        super().__init__(id)
        self.attribute_pair = attrpair
        self.priority=3
    ### checkEDGE has passthrough behavior
    # It simply checks whether the token has a compatible attrpair
    # Then duplicates and passes it on

    def __str__(self):
        v = ['*'+str(i)+'.'+x for i,x in enumerate(self.attribute_pair)]
        return '--'.join(v)

    def passthrough_fail_message(self):
        return 'Evaluation failed!'

    def entry_check(self,token):
        if('attr1' in token.keys() and 'attr2' in token.keys()):
            return (token['attr1'],token['attr2'])==self.attribute_pair
        return False

    def process_token(self,token,sender,verbose=False):
        tokens_to_pass = []
        passthrough_fail = ''
        evaluate = self.evaluate_token(token)
        if evaluate:
            if token['attr1']==token['attr2']:
                kmap= {'node1':'node2','attr1':'attr2','node2':'node1','attr2':'attr1'}
                tokens_to_pass = [new_token(token),new_token(token,keymap=kmap)]
            else:
                tokens_to_pass = [new_token(token)]
        else:
            passthrough_fail = self.passthrough_fail_message()
        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass,passthrough_fail=passthrough_fail))
        return tokens_to_pass

class store(SingleInputNode):
    def __init__(self,id=None,number_of_variables=1):
        super().__init__(id)
        self._register = TokenRegister()
        self._number_of_variables = number_of_variables
        self.priority = 2

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
    # depending on whether token is Add or Remove,
    # they update their register,
    # then pass out their updated register tokens.
    # if a token is null-add or null-remove, they don't update register
    # they just convert it with keymap and pass it on

    def entry_check(self,token):
        return all([x in token for x in self.keys()])

    def process_token(self,token,sender,verbose):
        token_type = token.get_type()
        subtoken = token.get_subtoken(self.keys())
        existing_token = self._register.get(subtoken)
        tokens_to_pass = []
        tokens_to_add = []
        tokens_to_remove = []
        passthrough_fail = ''

        if token_type=='add' and existing_token is None:
            tokens_to_add = [new_token(subtoken)]
            tokens_to_pass = [new_token(subtoken)]
        # Remove token if existing_token is not None and type is 'remove'
        elif token_type=='remove' and existing_token is not None:
            tokens_to_remove = [existing_token]
            tokens_to_pass = [new_token(existing_token,invert=True)]
        else:
            # do nothing
            passthrough_fail = self.passthrough_fail_message(token)

        # implement changes
        for token in tokens_to_add:
            self._register.add_token(token)
        for token in tokens_to_remove:
            self._register.remove_token(token)

        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass,tokens_to_add,tokens_to_remove,passthrough_fail))
        return tokens_to_pass

    def passthrough_fail_message(self,token):
        if token.get_type()=='add':
            return 'Token already found in register. Cannot add again!'
        if token.get_type()=='remove':
            return 'Token not found in register. Cannot remove!'
        return ''

    def filter(self,token):
        return self._register.filter(token)

    def filter_request(self,token):
        return self.filter(token)

    def select_random(self,n=1):
        return self._register.select_random(n)

    def count(self):
        return len(self._register)

class alias(SingleInputNode):
    def __init__(self,var_tuple,id=None):
        super().__init__(id)
        self.variable_names = var_tuple
        self.keymap = dict()
        self.reverse_keymap = dict()
        self.priority=1

    def set_keymap(self,key,value):
        self.keymap[key] = value
        self.reverse_keymap[value] = key
        return self

    def __str__(self):
        return ','.join(list(self.variable_names))

    def __len__(self):
        return len(list(self.predecessors)[0])

    def __lt__(self, other):
        return self.variable_names < other.variable_names

    def entry_check(self,token):
        if any([x is None for x in token.values()]):
            return False
        return True

    def transform_token(self,token,keymap,invert=False):
        return new_token(token,keymap=keymap,subsetkeys=keymap.keys(),invert=invert)

    ### alias is PASSTHROUGH with a twist
    # it has to use an internal keymap to transform the incoming token first

    def process_token(self,token,sender,verbose):
        transformed_token = self.transform_token(token,keymap=self.keymap)
        return super().process_token(transformed_token,sender,verbose)

    def passthrough_fail_message(self):
        return 'Somthing wrong with aliasing!'

    def filter(self,token):
        predecessor = list(self.predecessors)[0]
        return predecessor.filter_request(token)

    def filter_request(self,token):
        newtoken = new_token(token,keymap=self.reverse_keymap,subsetkeys=list(self.reverse_keymap.keys()))
        results = self.filter(newtoken)
        new_results = [new_token(x,keymap=self.keymap) for x in results]
        return set(new_results)

    def select_random(self,n=1):
        predecessor = list(self.predecessors)[0]
        return predecessor.select_random(n)

    def count(self):
        predecessor = list(self.predecessors)[0]
        return predecessor.count()

class is_not_in(alias):
    def __str__(self):
        return 'not '+ ','.join(list(self.variable_names))

    def process_token(self,token,sender,verbose=False):
        tokens_to_pass = []
        passthrough_fail = ''
        evaluate = self.evaluate_token(token)

        transformed_token = self.transform_token(token,keymap=self.keymap,invert=True)

        if evaluate:
            if token.get_type()=='add':
                # if incoming token is 'add', then the not-in condition fails
                # invert, then pass
                tokens_to_pass = [transformed_token]
            if token.get_type()=='remove':
                # if incoming token is 'remove', then we have to additionally check
                # if no remaining matching subtoken exists.
                # if so, then we can invert and pass
                predecessor = list(self.predecessors)[0]
                if len(self.filter_request(transformed_token)) > 0:
                    tokens_to_pass = [transformed_token]
        else:
            passthrough_fail = self.passthrough_fail_message()
        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass,passthrough_fail=passthrough_fail))
        return tokens_to_pass

    def filter_request(self,token):
        # filter request for is_not_in works differently
        # it takes current token, transforms, filters and gets results like a regular alias node
        # then it checks if results set is empty, which would satisfy not_in condition,
        # if so it returns the same token.
        # however, if the results set is non-empty, which breaks the not_in condition,
        # it returns empty
        newtoken = new_token(token,keymap=self.reverse_keymap,subsetkeys=list(self.reverse_keymap.keys()))
        results = self.filter(newtoken)
        if len(results)==0:
            return set([token])
        return set()

class merge(ReteNode):
    def __init__(self,var_tuple,id=None):
        super().__init__(id)
        self.variable_names = var_tuple
        self._register = TokenRegister()
        self.priority = 4

    def __str__(self):
        return ','.join(self.variable_names)

    def __len__(self):
        return len(self._register)

    def reduce_token(self,token):
        return new_token(token,subsetkeys=list(self.variable_names))

    def has(self,token):
        return len(self.filter(token)) > 0

    def filter(self,token):
        return self._register.filter(token)

    def filter_request(self,token):
        newtoken = new_token(token,subsetkeys=list(self.variable_names))
        return self.filter(newtoken)
    ### Merge does not have passthrough functionality.
    # depending on whether token is Add or Remove
    # they update their register
    # then pass out their updated register tokens
    def other_predecessor(self,sender):
        return list(self.predecessors.difference([sender]))[0]

    def entry_check(self,token):
        return all([x in self.variable_names for x in token.keys()])

    def process_token(self,token,sender,verbose):
        token_type = token.get_type()
        other_predecessor = self.other_predecessor(sender)
        tokens_to_pass = []
        tokens_to_add = []
        tokens_to_remove = []
        passthrough_fail = ''

        if token_type=='add' and not self.has(token):
            # pull tokens from other predecessor
            other_tokens = other_predecessor.filter_request(token)
            # merge, add and pass
            for tok in other_tokens:
                x = token.merge(tok)
                if x is not None:
                    tokens_to_add.append(new_token(x))
                    tokens_to_pass.append(new_token(x))
        elif token_type=='remove' and self.has(token):
            # remove existing tokens. invert and pass.
            existing_tokens = self.filter(token)
            tokens_to_remove = list(existing_tokens)
            tokens_to_pass = [new_token(x,invert=True) for x in existing_tokens]
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

    def select_random(self,n=1):
        return self._register.select_random(n)

    def count(self):
        return len(self._register)

class Complex(ReteNode):
    def __init__(self,id=None):
        super().__init__(id)
        self._index = EulerTourIndex()
        self.priority = 1

    def node_exists(self,node):
        return self._index.get_mapped_tour(node) is not None
    def node_is_singleton(self,node):
        return len(self._index.get_mapped_tour(node).get_nodes())==1
    def add_node(self,node):
        self._index.create_new_tour_from_node(node)
        return self
    def remove_node(self,node):
        self._index.delete_existing_tour_from_node(node)
        return self
    def add_edge(self,edge):
        self._index.auglink(edge)
        return self
    def remove_edge(self,edge):
        self._index.augcut(edge)
        return self

    def process_token(self,token,sender,verbose):
        token_type = token.get_type()
        tokens_to_pass = []
        passthrough_fail = ''

        # Adding and removing singletons of nodes
        if 'node' in token:
            node = token['node']
            if token_type=='add' and not self.node_exists(node):
                self.add_node(node)
            if token_type=='remove':
                assert self.node_is_singleton(node)
                self.remove_node(node)

        # Adding and removing edges
        if 'node1' in token and 'node2' in token:
            edge = tuple([token[x] for x in ['node1','attr1','attr2','node2']])
            if token_type=='add':
                self.add_edge(edge)
            if token_type=='remove':
                self.remove_edge(edge)

        if verbose:
            print(self.verbose_mode_message(token,tokens_to_pass,passthrough_fail))
        return tokens_to_pass
