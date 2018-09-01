from utils import generate_id

class ReteNode(object):
    def __init__(self,id=None):
        if id is None:
            self.id = generate_id()

class SingleInputNode(ReteNode): pass

class Root(SingleInputNode):
    def __init__(self):
        self.id = 'root'

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

    def __str__(self):
        return ','.join(self.variable_names)
