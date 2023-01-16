# copied from Max Schmalts -  @whalekeykeeper for string algorithms class with john nerbonne
import graphviz


def get_paths(fst):
    return list(fst.paths().items())[0]



'''
Pynini has a string transducer representation that is formed as 
a sequence of markers; those can be of two types:
    1. Teminal node (a number of state);
    2. Arc (first tail, then head, input char (ord) and output char (ord)).
The first state to ever appear is the initial one.
Thus a graph representation would look like this:
    x1* x2  x3  x4          # Arc (x1 -- init)
    x2  x3  x5  x1          # Arc
    x2                      # Teminal node
    x3  x1  x6  x7          # Arc
    x5                      # Teminal node
'''
# lookup = {'Ä':'ħ'}
lookup = {}
def parse_graph(transducer):
    nodes = []
    edges = []
    for edge in str(transducer).strip().split('\n'):
        arc = edge.split('\t')
        # node
        if len(arc) == 1: nodes.append(arc[0])
        # arc
        elif len(arc) == 4:
            # chr(0) = '\x00' which is not accepted graphviz
            repr0 = chr(int(arc[2])) if arc[2] != '0' else 'ε'
            repr0 = lookup.get(repr0,repr0)
            repr1 = chr(int(arc[3])) if arc[3] != '0' else 'ε'
            repr1 = lookup.get(repr1,repr1)
            edges.append({
            'tail': arc[0],
            'head': arc[1],
            'desc': repr0 if (repr0 == repr1) else f'{repr0}:{repr1}'
        })
    return nodes, edges

def show_graph(transducer):
    nodes, edges = parse_graph(transducer)
    graph = graphviz.Digraph()
    # edges first so that graph goes in the correct direction
    for edge in edges:
        graph.edge(
            tail_name=edge['tail'],
            head_name=edge['head'],
            label=edge['desc'],
            arrowhead='empty',
            arrowsize='0.6',
            fontsize='12',
            shape='circle'
        )
    # terminal nodes
    for i, node in enumerate(nodes):
        graph.node(
            name=node,
            # style='filled',
            # fillcolor='lightgrey',
            shape='doublecircle',
        )
    # initial_node
    graph.node(
        name=edges[0]['tail'],
        style='bold'
    )
    graph.attr(
        layout='dot',
        size='12.0',
        rankdir='LR'
    )
    graph.node_attr['shape'] = 'circle'
    return graph