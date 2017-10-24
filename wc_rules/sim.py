from obj_model import core
from wc_rules.base import BaseClass
from wc_rules.query import NodeTypeQuery, NodeQuery

class SimulationState(core.Model):
    agents = core.OneToManyAttribute(BaseClass,related_name='ss_agent')
    nodequeries = core.OneToManyAttribute(NodeQuery,related_name='ss_nq')

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.nodetypequery= NodeTypeQuery()

    def add_nodequery(self,nq):
        self.nodequeries.append(nq)
        self.nodetypequery.register_new_nq(nq)
        return self

    def add_node_as_nodequery(self,node):
        self.add_nodequery( NodeQuery(query=node) )
        return self


def main():
    pass

if __name__=='__main__':
	main()
