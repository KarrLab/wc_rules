from palettable.colorbrewer.qualitative import Pastel1_9
from utils import GenericError

def get_colors(categories):
    if len(categories) > 9:
        GenericError('Too many categories.')
    cmap = Pastel1_9
    n = len(categories)
    x = cmap.hex_colors[:n]
    return dict(zip(list(categories),x))

def generate_gml_node(idx, label ,fill):
    graphics = " graphics [ hasOutline 0 fill \"" + fill + "\" ] "
    labelgraphics = " LabelGraphics [text \"" + label + "\" ] "
    nodetext = "node [id " + str(idx) + graphics + labelgraphics + " ] "
    return nodetext

def generate_gml_edge(source,target):
    st_text = "source " + str(source) + " target " + str(target)
    graphics = " graphics [ fill \"#999999\" targetArrow \"standard\" ] "
    edgetext = "edge [ " + st_text + graphics + " ] "
    return edgetext

def generate_gml(node_labels,edge_tuples,node_categories=None):
    # node_labels is a id:label dict
    # node_categories is a id:category dict
    # edge_tuples is a list of (id1,id2) tuples
    if node_categories is None:
        node_categories = { x:1 for x in node_labels}
    cmap = get_colors(sorted(set(node_categories.values())))
    nodelines, edgelines = list(), list()
    for x in node_labels:
        label = node_labels[x]
        fill = cmap[node_categories[x]]
        nodelines.append(generate_gml_node(x,label,fill))
    for x,y in edge_tuples:
        edgelines.append(generate_gml_edge(x,y))
    graphtext = "graph\n[\n directed 1"
    alltexts = [graphtext] + nodelines + edgelines + ["]\n"]
    final_text = '\n'.join(alltexts)
    return final_text
