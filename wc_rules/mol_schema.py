""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import graph_utils
from wc_rules import rate_law
from wc_rules import schema
from wc_rules import utils
import obj_model.core
import wc_rules.exceptions


###### Structures ######
class BaseClass(obj_model.core.Model):
    """ Base class for chem_schema objects.

    Attributes:
        id (:obj:`str`): unique id that can be used to pick object from a list
    """
    id = obj_model.core.StringAttribute(primary=True, unique=True)

    class GraphMeta(graph_utils.GraphMeta):
        outward_edges = tuple()
        semantic = tuple()

    @property
    def label(self):
        """ Name of the class of the object

        :getter: Get the name of class of the object
        :type: :obj:`str`
        """
        return self.__class__.__name__

    ##### Graph Methods #####
    def get_graph(self, recurse=True, memo=None):
        return graph_utils.get_graph(self, recurse=recurse, memo=memo)


class Complex(BaseClass):

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple(['molecules'])
        semantic = tuple()

    def add(self, other):
        if isinstance(other, list):
            map(self.add, other)
        elif isinstance(other, Molecule):
            self.molecules.append(other)
        else:
            raise wc_rules.exceptions.AddObjectError(self, other, [Molecule])
        return self


class Molecule(BaseClass):
    complex = obj_model.core.ManyToOneAttribute(Complex, related_name='molecules')

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple(['sites'])
        semantic = tuple()

    def add(self, other):
        if isinstance(other, list):
            map(self.add, other)
        elif isinstance(other, Site):
            self.sites.append(other)
        else:
            raise wc_rules.exceptions.AddObjectError(self, other, [Site])
        return self


class Site(BaseClass):
    molecule = obj_model.core.ManyToOneAttribute(Molecule, related_name='sites')

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple(['boolvars', 'pairwise_overlap', 'binding_state'])
        semantic = tuple()

    def add(self, other, where=None):
        if where is None or where == 'boolvars':
            return self.add_boolvars(other)
        elif where == 'overlaps':
            return self.add_pairwise_overlap_targets(other)
        elif where == 'bond':
            return self.add_bond(other)

    #### Boolean Variables ####
    def add_boolvars(self, vars):
        for var in utils.listify(vars):
            if not isinstance(var, BooleanStateVariable):
                raise wc_rules.exceptions.AddObjectError(self, var, [BooleanStateVariable])
            self.boolvars.append(var)
        return self

    #### Pairwise Overlaps ####
    def init_pairwise_overlap(self):
        self.pairwise_overlap = PairwiseOverlap(source=self)
        return self

    def add_pairwise_overlap_targets(self, targets, mutual=True):
        if self.pairwise_overlap is None:
            self.init_pairwise_overlap()
        if mutual:
            for target in targets:
                if target.pairwise_overlap is None:
                    target.init_pairwise_overlap()
        self.pairwise_overlap.add_targets(targets, mutual=mutual)
        return self

    def remove_pairwise_overlap_targets(self, targets):
        return self.pairwise_overlap.remove_targets(targets)

    def undef_pairwise_overlap(self):
        targets = [t for t in self.pairwise_overlap.targets]
        self.remove_pairwise_overlap_targets(targets)
        self.pairwise_overlap = None
        return self

    def get_overlaps(self):
        if self.pairwise_overlap is None:
            return None
        if self.pairwise_overlap.get_num_targets() == 0:
            return None
        return self.pairwise_overlap.targets

    def has_overlaps(self):
        if self.pairwise_overlap is not None:
            if self.pairwise_overlap.get_num_targets() > 0:
                return True
        return False

    #### Binding State ####
    def init_binding_state(self):
        self.binding_state = BindingState(source=self)
        return self

    def add_bond(self, target):
        if self.binding_state is None:
            self.init_binding_state()
        if target.binding_state is None:
            target.init_binding_state()
        if self.get_binding_state_value() == 'bound':
            raise wc_rules.exceptions.Error('Another bond already exists!')
        if target.get_binding_state_value() == 'bound':
            raise wc_rules.exceptions.Error('Another bond already exists!')
        self.binding_state.add_targets(target)

    def remove_bond(self):
        targets = [t for t in self.binding_state.targets]
        return self.binding_state.remove_targets(targets)

    def undef_binding_state(self):
        self.remove_bond()
        self.binding_state = None
        return self

    def get_binding_partner(self):
        if self.binding_state is None:
            return None
        return self.binding_state.targets[0]

    def get_binding_state_value(self):
        if self.binding_state is None:
            return None
        if self.binding_state.get_num_targets() == 0:
            return 'unbound'
        if self.binding_state.get_num_targets() == 1:
            return 'bound'


###### Site to Site Relationships ######
class SiteRelationsManager(BaseClass):
    source = obj_model.core.OneToOneAttribute(Site)
    targets = obj_model.core.ManyToManyAttribute(Site)
    attrname = obj_model.core.StringAttribute()

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple(['targets'])
        semantic = tuple()

    def add_targets(self, targets, mutual=True):
        for target in utils.listify(targets):
            self.targets.append(target)
            if mutual:
                getattr(target, self.attrname).add_targets([self.source], mutual=False)
        return self

    def remove_targets(self, targets, mutual=True):
        for target in utils.listify(targets):
            self.targets.remove(target)
            if mutual:
                getattr(target, self.attrname).remove_targets([self.source], mutual=False)
        return self

    def get_num_targets(self):
        if self.targets is None:
            return 0
        return len(self.targets)


class PairwiseOverlap(SiteRelationsManager):
    source = obj_model.core.OneToOneAttribute(Site, related_name='pairwise_overlap')
    targets = obj_model.core.ManyToManyAttribute(Site, related_name='pairwise_overlap_targets')
    attrname = obj_model.core.StringAttribute(default='pairwise_overlap')


class BindingState(SiteRelationsManager):
    source = obj_model.core.OneToOneAttribute(Site, related_name='binding_state')
    targets = obj_model.core.ManyToManyAttribute(Site, related_name='binding_state_targets', max_related=1, max_related_rev=1)
    attrname = obj_model.core.StringAttribute(default='binding_state')

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple(['targets'])
        semantic = tuple(['get_num_targets'])


###### Variables ######
class BooleanStateVariable(BaseClass):
    site = obj_model.core.ManyToOneAttribute(Site, related_name='boolvars')
    value = obj_model.core.BooleanAttribute(default=None)

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple()
        semantic = tuple(['value'])

    def set_value(self, value):
        self.value = value
        return self

    def set_true(self): 
        return self.set_value(True)

    def set_false(self): 
        return self.set_value(False)


###### Operations ######
class Operation(BaseClass):

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple(['target'])
        semantic = tuple()

    @property
    def target(self): 
        return None

    @target.setter
    def target(self, value): 
        return None

    def set_target(self, value):
        self.target = value
        return self


class BondOperation(Operation):
    sites = obj_model.core.OneToManyAttribute(Site, related_name='bond_op')

    @property
    def target(self): return self.sites

    @target.setter
    def target(self, arr):
        self.sites = arr

    def set_target(self, other):
        if isinstance(other, list):
            map(self.set_target, other)
        elif isinstance(other, Site):
            self.sites.append(other)
        else:
            raise wc_rules.exceptions.AddObjectError(self, other, [Site], method_name='set_target')
        return self


class AddBond(BondOperation):
    pass


class DeleteBond(BondOperation):
    pass


class BooleanStateOperation(Operation):
    boolvar = obj_model.core.ManyToOneAttribute(BooleanStateVariable, related_name='boolean_state_ops')

    @property
    def target(self): return self.boolvar

    @target.setter
    def target(self, boolvar):
        self.boolvar = boolvar

    def set_target(self, other):
        if isinstance(other, BooleanStateVariable):
            self.boolvar = other
        else:
            raise wc_rules.exceptions.AddObjectError(self, other, [BooleanStateVariable], method_name='set_target')
        return self


class SetTrue(BooleanStateOperation):
    pass


class SetFalse(BooleanStateOperation):
    pass


##### Rules #####
class Rule(BaseClass):
    reactants = obj_model.core.OneToManyAttribute(Complex, related_name='rule')
    reversible = obj_model.core.BooleanAttribute(default=False)
    operations = obj_model.core.OneToManyAttribute(Operation, related_name='rule')
    forward = obj_model.core.OneToOneAttribute(rate_law.RateExpression, related_name='rule_forward')
    reverse = obj_model.core.OneToOneAttribute(rate_law.RateExpression, related_name='rule_reverse')

    class GraphMeta(BaseClass.GraphMeta):
        outward_edges = tuple(['reactants', 'operations'])
        semantic = tuple()

    def add(self, other):
        if isinstance(other, list):
            map(self.add, other)
        elif isinstance(other, Complex):
            self.reactants.append(other)
        elif isinstance(other, Operation):
            self.operations.append(other)
        else:
            raise wc_rules.exceptions.AddObjectError(self, other, [Complex, Operation])
        return self
