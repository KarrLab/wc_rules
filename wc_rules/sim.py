from obj_model import core
from wc_rules.base import BaseClass
from wc_rules.query import NodeTypeQuery, NodeQuery, GraphQuery
from collections import deque

class UpdateMessage(dict):
    def __init__(self,*args,**kwargs):
        validkeys = 'update_attr update_type instance nodequery graphquery'.split()
        for kwarg in kwargs:
            if kwarg not in validkeys:
                raise KeyError(kwarg+' not a valid key.')
        remaining_keys = set(validkeys) - set(kwargs.keys())
        for kwarg in remaining_keys:
                kwargs[kwarg] = None
        super().__init__(*args,**kwargs)

class SimulationState(core.Model):
    agents = core.OneToManyAttribute(BaseClass,related_name='ss_agent')
    nodequeries = core.OneToManyAttribute(NodeQuery,related_name='ss_nq')
    nodetypequery = core.OneToOneAttribute(NodeTypeQuery,related_name='ss_ntq')
    graphqueries = core.OneToManyAttribute(GraphQuery,related_name='ss_gq')

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.nodetypequery= NodeTypeQuery()
        self.update_message_queue = deque()

    def add_nodequery(self,nq):
        self.nodequeries.append(nq)
        self.nodetypequery.register_new_nq(nq)
        return self

    def add_node_as_nodequery(self,node):
        self.add_nodequery( NodeQuery(query=node) )
        return self

    def add_graphquery(self,nqs):
        gq = GraphQuery()
        for nq in nqs:
            self.add_nodequery(nq)
            gq.add_nodequery(nq)
        gq.compile_traversal_functions()
        self.graphqueries.append(gq)
        return self

    def add_as_graphquery(self,nodes):
        self.add_graphquery([NodeQuery(query=x) for x in nodes])
        return self



def main():
    pass

if __name__=='__main__':
	main()
