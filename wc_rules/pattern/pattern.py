
from ..utils.validate_helpers import *
from ..utils.data_structures import DictLike
from ..utils.utils import split_string, check_cycle, idgen
from ..expr.executable_expr import Constraint, Computation, initialize_from_string

class GraphContainer(DictLike):
    # A temporary container for a graph that can be used to create
    # canonical forms or iterate over a graph

    def __init__(self,_list=[]):
        # there must be only one way to create a GraphContainer and that must be to create a list
        super().__init__(_list)

    def iternodes(self):
        for idx, node in self._dict.items():
            yield idx,node

    def iteredges(self):
        edges_visited = set()
        for idx,node in self.iternodes():
            for attr in node.get_related_attributes(ignore_None=True):
                related_attr = node.get_related_name(attr)
                for related_node in node.listget(attr):
                    edge = [(node.id, attr), (related_node.id,related_attr)]
                    edge = tuple(sorted(edge))
                    if edge not in edges_visited:
                        edges_visited.add(edge)
                        yield edge

    def update(self):
        idx,root = list(self._dict.items())[0]
        for node in root.get_connected():
            self.add(node)

    def duplicate(self,varmap={},include=None):
        if include is None:
            include = self.keys()

        newnodes = dict()
        for idx,node in self.iternodes():
            if idx not in include:
                continue
            idx = varmap.get(idx,idx)
            newnodes[idx] = node.duplicate(id=idx)

        for (idx1,attr1),(idx2,attr2) in self.iteredges():
            if idx1 not in include or idx2 not in include:
                continue
            idx1, idx2 = [varmap.get(x,x) for x in [idx1,idx2]]
            newnodes[idx1].safely_add_edge(attr1,newnodes[idx2])
        return GraphContainer(newnodes.values())

    def strip_attrs(self):
        attrs = dict()
        for idx,node in self.iternodes():
            attrs[idx] = node.get_literal_attrdict()
            for attr in attrs[idx]:
                setattr(node,attr,None)
        return self,attrs

    def validate_connected(self):
        err = "GraphContainer does not hold a connected graph."
        assert len(self) == 0 or GraphContainer(self.values()[0].get_connected())==self, err

    @property
    def variables(self):
        return self.keys()

    @property
    def namespace(self):
        return {idx:node.__class__ for idx,node in self._dict.items()}
    
    def add_suffix(self,suffix):
        varmap = {x:f'{x}_{suffix}' for x in self.keys()}
        return self.duplicate(varmap=varmap)
    	
class Pattern:

	def __init__(self, parent=GraphContainer(), helpers=dict(), constraints = [], params= []):
		self.validate_parent(parent)
		self.parent = parent

		self.validate_helpers(helpers)
		self.helpers = helpers

		self.validate_params(params)
		self.params = params
		
		self.assigned_variables = self.validate_constraints(constraints)
		self.constraints = constraints

	@property
	def variables(self):
		return list(self.namespace.keys())
	
	@property
	def namespace(self):
		d = dict()
		d.update(self.parent.namespace)
		for h in self.helpers:
			d[h] = "Helper Pattern"
		for p in self.params:
			d[p] = "Parameter"
		for v  in self.assigned_variables:
			d[v] = "Assigned Variable"
		return d

	def asdict(self):
		return dict(**self.namespace,constraints=self.constraints)

	def validate_parent(self,parent):
		validate_class(parent,(GraphContainer,Pattern),'Parent')
		if isinstance(parent,GraphContainer):
			parent.validate_connected()
			validate_keywords(parent._dict.keys(),'Parent Variable')
			for idx,node in parent.iternodes():
				validate_literal_attributes(node)
				validate_related_attributes(node)

	def validate_helpers(self,helpers):
		validate_class(helpers,dict,'Helpers')
		validate_keywords(helpers.keys(),'Helper')
		validate_unique(self.parent.variables,helpers.keys(),'Helper')
		validate_dict(helpers,Pattern,'Helper')
		
	def validate_params(self,params):
		validate_class(params,list,'Parameters')
		validate_keywords(params,'Parameter')
		validate_unique(self.parent.variables + list(self.helpers.keys()), params, 'Parameter')
		
	def validate_constraints(self,constraints):
		validate_class(constraints,list,'Constraints')
		validate_list(constraints,str,'Constraint')

		namespace = self.parent.variables + list(self.helpers.keys()) + self.params
		newvars, kwdeps = [] , {}
		for s in constraints:
			x = initialize_from_string(s,(Constraint,Computation))
			validate_contains(namespace + newvars,x.keywords,'Variable')
			if isinstance(x,Computation):
				v = x.deps.declared_variable
				validate_keywords([v],'Variable')
				validate_unique(namespace + newvars,[v],'Variable')
				newvars.append(v)
				kwdeps[v] = x.keywords
		validate_acyclic(kwdeps)
		return newvars

class SynthesisPattern:

	def __init__(self,prototype):
		err = "FactoryPattern must be initialized from a GraphContainer with a connected graph."
		assert isinstance(prototype,GraphContainer) and prototype.validate_connected(), err
		self.prototype = prototype

