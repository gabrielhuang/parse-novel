# -*- coding: utf-8 -*-
from matplotlib.pylab import cm


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