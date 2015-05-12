# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pylab import cm

def draw_graph(graph, labels=None, edge_size=None, graph_layout='shell',
               node_size=1600, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):

    # create networkx graph
    G=nx.Graph()

    # add edges
    for edge in graph:
        G.add_edge(edge[0], edge[1])

    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)

    # draw graph
    nx.draw_networkx_nodes(G,graph_pos,node_size=node_size, 
                           alpha=node_alpha, node_color=node_color)
    nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                            font_family=text_font)

    if labels is None:
        labels = [1]*len(graph)
        
    if edge_size is None:
        edge_size = [1]*len(graph)
        
    edge_labels = dict(zip(graph, labels))
    nx.draw_networkx_edges(G,graph_pos,alpha=0.5,width=labels, edge_color='m')    
    nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels, 
                                 label_pos=edge_text_pos)


    # show graph
    plt.show()


def tuple_to_rgba(components):
    acc = ['#']+['{:02x}'.format(int(255.*max(min(x, 1.), 0.))) for x in components]
    return ''.join(acc)
    

def transparent_gray(x):
    '''
    Return black  #000000FF if 1 and transparent #00000000 if 0
    '''
    return tuple_to_rgba(0., 0., 0., x)
    
    
def transparent_jet(x):
    '''
    Uses jet colormap
    '''
    cmap = list(cm.jet(x))
    cmap[3] = x # alpha channel
    return tuple_to_rgba(cmap)
    
    
    
def draw_graphviz(edges, weights, smallest=1., get_color=transparent_jet):
    '''
    Prepares a weighted undirected graph for Graphviz Neato rendering
    http://www.graphviz.org/pdf/neatoguide.pdf
    '''
    lines = ['graph G {']
    lines.append('splines=true') # deflect edges if overlap with nodes
    lengths = 1./(1.+weights)
    lengths = smallest * lengths / lengths.min()
    max_weight = weights.max()
    for edge, weight, length in zip(edges, weights, lengths):
        lines.append('{} [penwidth={}, len={}, color="{}"]'.format(
        '"'+edge[0]+'" -- "'+edge[1]+'"', weight, length, get_color((1+weight)/(1+max_weight))))
    lines.append('}')
    return '\n'.join(lines)

if __name__=='__main__':
    graph = [(0, 1), (1, 5), (1, 7), (4, 5), (4, 8), (1, 6), (3, 7), (5, 9),
             (2, 4), (0, 4), (2, 5), (3, 6), (8, 9)]
    
    # you may name your edge labels
    labels = map(chr, range(65, 65+len(graph)))
    #draw_graph(graph, labels)
    
    # if edge labels is not specified, numeric labels (0, 1, 2...) will be used
    draw_graph(graph)