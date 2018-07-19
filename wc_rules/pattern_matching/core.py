
class WorkingMemoryGraph(object):
    def __init__(self):
        self.nodes = dict()

    def add_node(self,node):
        self.nodes[node.get_id()] = node
        return self

    def retrieve_node(self,idx):
        return self.nodes[idx]

    def __str__(self):
        return self.nodes.__str__()
