"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-04-20
:Copyright: 2017, Karr Lab
:License: MIT
"""
from obj_model import core
from wc_rules import base,entity,utils


class Molecule(entity.Entity):pass

class Site(entity.Entity):
    molecule = core.ManyToOneAttribute(Molecule,related_name='sites')

class SiteRelation(entity.Entity):
    sources = core.OneToManyAttribute(Site,related_name='site_relations')
    targets = core.OneToManyAttribute(Site,related_name='site_relations_targets')
    n_max_sources = None
    n_max_targets = None

    def add_sources(self,*args):
        if self.n_max_sources is not None:
            if len(self.sources)+len(args) > self.n_max_sources:
                raise utils.AddError('Number of source sites allowed for this relation will be exceeded.')
        for arg in args:
            self.sources.append(arg)
        return self

    def add_targets(self,*args):
        if self.n_max_targets is not None:
            if len(self.targets)+len(args) > self.n_max_targets:
                raise utils.AddError('Number of target sites allowed for this relation will be exceeded.')
        for arg in args:
            self.targets.append(arg)
        return self


class UndirectedSiteRelation(SiteRelation):
    n_max_targets = 0
    def add_sites(self,*args):
        self.add_sources(*args)
        return self

class Bond(UndirectedSiteRelation):
    n_max_sources = 2

class Overlap(UndirectedSiteRelation):
    n_max_sources = 2

class DirectedSiteRelation(SiteRelation):pass
