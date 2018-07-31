from wc_rules.indexer import Index_By_ID
from wc_rules.utils import listify,generate_id
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
        return node.get_id() in self._nodes

    def add_node(self,node,recurse=True):
        if node in self:
            return self
        self._nodes.append(node)
        if recurse:
            for attr in node.get_related_attributes(none_allowed=False):
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
            attrs = node.get_related_attributes(none_allowed=True)
            for attr in attrs:
                val = getattr(node,attr,None)
                if val is None:
                    setattr(new_node,attr,None)
                elif node.attribute_properties[attr]['append']:
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


def main():
    pass

if __name__ == '__main__':
    main()
