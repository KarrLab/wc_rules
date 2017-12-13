""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-04-06
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
from wc_rules import base
from wc_rules import entity
from wc_rules import ratelaw
from wc_rules import utils
from wc_rules import variables


class Complex(entity.Entity):

    class GraphMeta(base.BaseClass.GraphMeta):
        outward_edges = tuple(['molecules'])
        semantic = tuple()

    def get_molecule(self, label, **kwargs):
        if label is not None:
            return self.molecules.get(label=label, **kwargs)
        else:
            return self.molecules.get(**kwargs)


class Molecule(entity.Entity):
    complex = core.ManyToOneAttribute(Complex, related_name='molecules')

    class GraphMeta(base.BaseClass.GraphMeta):
        outward_edges = tuple(['sites'])
        semantic = tuple()

    def get_site(self, label, **kwargs):
        if label is not None:
            return self.sites.get(label=label, **kwargs)
        else:
            return self.sites.get(**kwargs)

    def compute_overlaps(self):
        return self


class Site(entity.Entity):
    molecule = core.ManyToOneAttribute(Molecule, related_name='sites')
    bond = core.OneToOneAttribute('Site', related_name='bond')
    overlaps = core.ManyToManyAttribute('Site', related_name='overlaps')
    boolvars = core.OneToManyAttribute(variables.BooleanVariable, related_name='site')

    class GraphMeta(base.BaseClass.GraphMeta):
        outward_edges = tuple(['bond', 'overlaps', 'boolvars'])
        semantic = tuple()

    available_to_bind = core.BooleanAttribute(default=True)

    def sync_binding_state(self):
        if self.available_to_bind is True:
            if self.bond is not None or any(x.bond is not None for x in self.overlaps):
                self.available_to_bind = False
        if self.available_to_bind is False:
            if self.bond is None and all(x.bond is None for x in self.overlaps):
                self.available_to_bind = True
        return self

    #### Boolean Variables ####
    def get_boolvar(self, label, **kwargs):
        if label is not None:
            return self.boolvars.get(label=label, **kwargs)
        else:
            return self.boolvars.get(**kwargs)

    #### Pairwise Overlaps ####
    def add_overlaps(self, other_sites, mutual=True):
        return self.add_by_attrname(other_sites, 'overlaps')

    def remove_overlaps(self, other_sites):
        return self.remove_by_attrname(other_sites, 'overlaps')

    def undef_overlaps(self):
        # :todo:(Sekar) Review this. Previously, overlaps was being set to None. However, None is not compatible with obj_model.
        self.overlaps = []
        return self

    def get_overlaps(self):
        return self.overlaps

    def has_overlaps(self):
        # :todo:(Sekar) Review this. Previously, this was checking if overlaps was None. However, None is not compatible with obj_model.
        return len(self.overlaps) > 0

    #### Binding State ####
    def undef_binding_state(self):
        self.bond = None
        return self

    def add_unbound_state(self):
        self.bond = self
        return self

    def add_bond_to(self, target):
        for x in [self, target]:
            x.undef_binding_state()
        self.bond = target
        return self

    def remove_bond(self):
        other = self.bond
        for x in [self, other]:
            x.undef_binding_state()
            x.add_unbound_state()
        return self

    @property
    def binding_state_value(self):
        if self.bond is None:
            return
        elif self.bond is self:
            return 'unbound'
        else:
            return 'bound'

    def get_binding_partner(self):
        if self.bond is not None:
            if self.bond is self:
                return
        return self.bond

###### Operations ######
class Operation(base.BaseClass):

    class GraphMeta(base.BaseClass.GraphMeta):
        outward_edges = tuple(['target'])
        semantic = tuple()

    @property
    def target(self):
        return

    @target.setter
    def target(self, value):
        return

    def set_target(self, value):
        self.target = value
        return self


class BondOperation(Operation):
    sites = core.OneToManyAttribute(Site, related_name='bond_op')

    @property
    def target(self):
        return self.sites

    @target.setter
    def target(self, arr):
        self.sites = arr

    def set_target(self, v):
        if isinstance(v, list):
            for vv in v:
                self.set_target(vv)
        elif isinstance(v, Site):
            self.sites.append(v)
        else:
            raise utils.AddObjectError(self, v, ['Site'], 'set_target()')
        return self


class AddBond(BondOperation):
    pass


class DeleteBond(BondOperation):
    pass


class BooleanStateOperation(Operation):
    boolvar = core.OneToOneAttribute(variables.BooleanVariable, related_name='boolean_op')

    @property
    def target(self):
        return self.boolvar

    @target.setter
    def target(self, boolvar):
        self.boolvar = boolvar

    def set_target(self, v):
        if isinstance(v, variables.BooleanVariable):
            self.boolvar = v
        else:
            raise utils.AddObjectError(self, v, ['BooleanStateVariable'], 'set_target()')
        return self


class SetTrue(BooleanStateOperation):
    pass


class SetFalse(BooleanStateOperation):
    pass

##### Rule #####
class Rule(base.BaseClass):
    reactants = core.OneToManyAttribute(Complex, related_name='rule')
    reversible = core.BooleanAttribute(default=False)
    operations = core.OneToManyAttribute(Operation, related_name='rule')
    forward = core.OneToOneAttribute(ratelaw.RateExpression, related_name='rule_forward')
    reverse = core.OneToOneAttribute(ratelaw.RateExpression, related_name='rule_reverse')

    class GraphMeta(base.BaseClass.GraphMeta):
        outward_edges = tuple(['reactants', 'operations'])
        semantic = tuple()
