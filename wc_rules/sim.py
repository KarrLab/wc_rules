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
        self.verbose = False

    def add_message(self,update_message):
        # appends to the right of deque
        self.update_message_queue.append(update_message)
        return self

    def pop_message(self):
        # removes from left of deque
        msg = self.update_message_queue.popleft()
        return msg

    def process_message(self,update_message):
        # processes and returns a list of messages
        if self.verbose:
            print('processing message ',update_message.__str__())
        update_attr = update_message['update_attr']
        update_type = update_message['update_type']
        msgs = []
        if update_attr == 'instance':
            instance = update_message['instance']
            for nq in self.nodetypequery[instance.__class__]:
                msgs.extend(self.generate_nodequery_message(nq,instance))
        if update_attr == 'nodequery':
            instance = update_message['instance']
            nq = update_message['nodequery']
            if update_type == 'add':
                nq.add_match(instance)
                msgs.extend(self.generate_graphquery_message(nq,instance,'add'))
            if update_type == 'remove':
                nq.remove_match(instance)
                msgs.extend(self.generate_graphquery_message(nq,instance,'remove'))
        if update_attr == 'graphquery':
            instance = update_message['instance']
            nq = update_message['nodequery']
            gq = update_message['graphquery']
            if update_type == 'add':
                gq.seed_graphmatches([(nq,instance)])
                gq.process_partial_matches()
            if update_type == 'remove':
                gq.remove_graphmatches([(nq,instance)])
        return msgs

    def generate_nodequery_message(self,nq,instance):
        # returns a message
        match_verified = nq.verify_match(instance)
        if match_verified and instance not in nq.matches:
            return [UpdateMessage(update_attr='nodequery',update_type='add',nodequery=nq,instance=instance)]
        if not match_verified and instance in nq.matches:
            return [UpdateMessage(update_attr='nodequery',update_type='add',nodequery=nq,instance=instance)]
        return []

    def generate_graphquery_message(self,nq,instance,update_type):
        if nq.graphquery is not None:
            gq = nq.graphquery
            if update_type=='add':
                return [UpdateMessage(update_attr='graphquery',update_type='add',nodequery=nq,instance=instance,graphquery=gq)]
            if update_type=='remove':
                return [UpdateMessage(update_attr='graphquery',update_type='remove',nodequery=nq,instance=instance,graphquery=gq)]
        return []

    def process_message_queue(self):
        while len(self.update_message_queue)>0:
            current_message = self.pop_message()
            messages = self.process_message(current_message)
            for msg in messages:
                self.add_message(msg)
        return self

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
