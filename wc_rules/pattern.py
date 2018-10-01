from wc_rules.indexer import Index_By_ID, HashableDict
from wc_rules.utils import listify,generate_id
from operator import eq
import random
import pprint

class Pattern(object):
    def __init__(self,idx,nodelist=None,recurse=True):
        self.id = idx
        self._nodes = set()
        if nodelist is not None:
            for node in nodelist:
                self.add_node(node,recurse)

    def __contains__(self,node):
        return node in self._nodes

    def __iter__(self):
        return iter(self._nodes)

    def as_dict(self):
        return { x.id:x for x in self }

    def __getitem__(self,key):
        d = self.as_dict()
        return d[key]

    def add_node(self,node,recurse=True):
        if node in self:
            return self
        self._nodes.add(node)
        if recurse:
            for attr in node.get_nonempty_related_attributes():
                nodelist = listify(getattr(node,attr))
                for node2 in nodelist:
                    self.add_node(node2,recurse)
        return self

    def __str__(self):
        s = pprint.pformat(self) + '\n' + pprint.pformat(sorted(self._nodes,key=lambda x: (x.label,x.id)))
        return s

    def __len__(self): return len(self._nodes)

    def duplicate2(self,idx=None,preserve_ids=False):
        nodemap = {}
        if idx is None:
            idx = generate_id()
        new_pattern = self.__class__(idx)
        for idx,node in self._nodes.items():
            new_node = node.duplicate()
            nodemap[idx] = new_node.get_id()
            new_pattern.add_node(new_node)
        already_encountered = []
        for idx,node in self._nodes.items():
            new_node = new_pattern._nodes[nodemap[idx]]
            attrs = node.get_nonempty_related_attributes()
            for attr in attrs:
                if node.attribute_properties[attr]['append']:
                    setattr(new_node,attr,[])
                    for node2 in getattr(node,attr):
                        if node2.get_id() in already_encountered:
                            continue
                        x = getattr(new_node,attr)
                        node2_map = new_pattern._nodes[nodemap[node2.get_id()]]
                        x.append(node2_map)
                else:
                    node2 = getattr(node,attr)
                    if node2.get_id() in already_encountered:
                        continue
                    node2_map = new_pattern._nodes[nodemap[node2.get_id()]]
                    setattr(new_node,attr,node2_map)
            already_encountered.append(node.get_id())
        if preserve_ids:
            new_idx = list(new_pattern._nodes.keys())
            reverse_nodemap = {v:k for k,v in nodemap.items()}
            for idx in new_idx:
                x = new_pattern._nodes.pop(idx)
                x.set_id(reverse_nodemap[idx])
                new_pattern.add_node(x,recurse=False)
        return new_pattern

    def duplicate(self,idx=None,preserve_ids=False):
        if idx is None:
            idx = generate_id()
        new_pattern = self.__class__(idx)
        nodemap = dict()
        for node in self:
            # this duplicates upto scalar attributes
            new_node = node.duplicate(preserve_id=preserve_ids)
            nodemap[node.id] = new_node
            new_pattern.add_node(new_node,recurse=False)
        encountered = set()
        for node in self:
            attrcontents = node.generate_attr_contents()
            appendable = node.generate_appendability_dict()
            for attr in attrcontents:
                objs = set(attrcontents[attr]) - encountered
                if len(objs) == 0: continue
                new_objs = [nodemap[x.id] for x in objs]
                new_node = nodemap[node.id]
                if appendable[attr]:
                    new_attr = getattr(new_node,attr)
                    new_attr.extend(new_objs)
                else:
                    setattr(new_node,attr,new_objs.pop())
            encountered.add(node)
        return new_pattern


    def generate_queries_TYPE(self):
        ''' Generates tuples ('type',_class) '''
        type_queries = {}
        for node in self:
            idx = node.id
            type_queries[idx] = []
            list_of_classes = node.__class__.__mro__
            for _class in reversed(list_of_classes):
                if _class.__name__ in ['BaseClass','Model','object']:
                    continue
                v = ['type',_class]
                type_queries[idx].append(tuple(v))
        return type_queries

    def generate_queries_ATTR(self):
        ''' Generates tuples ('attr',attrname,operator,value) '''
        attr_queries = {}
        for node in self:
            idx = node.id
            attr_queries[idx] = []
            for attr in sorted(node.get_nonempty_scalar_attributes()):
                if attr=='id': continue
                v = ['attr',attr,eq,getattr(node,attr)]
                attr_queries[idx].append(tuple(v))
        return attr_queries

    def generate_queries_REL(self):
        ''' Generate tuples ('rel',idx1,attrname,related_attrname,idx2) '''
        rel_queries = []
        already_encountered = []
        for node in self:
            idx = node.id
            for attr in node.get_nonempty_related_attributes():
                nodelist = listify(getattr(node,attr))
                for node2 in nodelist:
                    if node2.id in already_encountered:
                        continue
                    related_attr = node.attribute_properties[attr]['related_attr']
                    # this is alphabetical comparison 'ab' < 'b'
                    if attr <= related_attr:
                            v = ['rel',idx,attr,related_attr,node2.id]
                    else:
                        v = ['rel',node2.id,related_attr,attr,idx]
                    rel_queries.append(tuple(v))
            already_encountered.append(idx)
        return rel_queries

    def generate_queries(self):
        return {
            'type': self.generate_queries_TYPE(),
            'attr': self.generate_queries_ATTR(),
            'rel': self.generate_queries_REL(),
        }

def main():
    pass


if __name__ == '__main__':
    main()
