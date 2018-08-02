from wc_rules.indexer import Index_By_ID
from wc_rules.utils import listify,generate_id
from operator import eq
import random
import pprint

class Pattern(object):
    def __init__(self,idx,nodelist=None,recurse=True):
        self.id = idx
        self._nodes = Index_By_ID()
        if nodelist is not None:
            for node in nodelist:
                self.add_node(node,recurse)

    def __contains__(self,node):
        return node in self._nodes

    def add_node(self,node,recurse=True):
        if node in self:
            return self
        self._nodes.append(node)
        if recurse:
            for attr in node.get_nonempty_related_attributes():
                nodelist = listify(getattr(node,attr))
                for node2 in nodelist:
                    self.add_node(node2,recurse)
        return self

    def __str__(self):
        s = pprint.pformat(self) + '\n' + pprint.pformat(self._nodes)
        return s

    def __len__(self): return len(self._nodes)

    def duplicate(self,idx=None,preserve_ids=False):
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

    def generate_queries_TYPE(self):
        type_queries = {}
        for idx,node in self._nodes.items():
            type_queries[idx] = []
            list_of_classes = node.__class__.__mro__
            for _class in reversed(list_of_classes):
                if _class.__name__ in ['BaseClass','Model','object']:
                    continue
                v = ['type',_class]
                type_queries[idx].append(tuple(v))
        return type_queries

    def generate_queries_ATTR(self):
        attr_queries = {}
        for idx,node in self._nodes.items():
            attr_queries[idx] = []
            for attr in node.get_nonempty_scalar_attributes():
                if attr=='id': continue
                v = ['attr',attr,eq,getattr(node,attr)]
                attr_queries[idx].append(tuple(v))
        return attr_queries

    def generate_queries_REL(self):
        rel_queries = []
        already_encountered = []
        for idx,node in self._nodes.items():
            for attr in node.get_nonempty_related_attributes():
                nodelist = listify(getattr(node,attr))
                for node2 in nodelist:
                    if node2.id in already_encountered:
                        continue
                    related_attr = node.attribute_properties[attr]['related_attr']
                    v = ['rel',idx,attr,related_attr,node2.id]
                    rel_queries.append(tuple(v))
            already_encountered.append(node.id)
        return rel_queries

def main():
    pass

if __name__ == '__main__':
    main()
