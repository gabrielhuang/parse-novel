# -*- coding: utf-8 -*-
'''
@brief Test application to export augmented novel
@date April 2015
@author Gabriel Huang
'''

import segmenter
import prettify
import NamedEntityIdentifier
import numpy as np
import people
import draw_graph
reload(segmenter)
reload(prettify)
reload(NamedEntityIdentifier)
reload(people)
reload(draw_graph)
from people import People, PeopleNoPos
from draw_graph import draw_graphviz

# choose whether to use part of speech tagging or not for character identification
PeopleClass = PeopleNoPos  # PeopleClass = People

# Load text
#txt_file = open('sherlock-pg1661.txt','r')
txt_file = open('data/gatsby.txt','r')
txt_file = open('data/hp.txt','r')
txt = txt_file.read().strip()
#txt = txt_file.read(100000).strip()[3000:]


# Get paragraphs and whether is it dialog or narrative
paragraphs, p_types = segmenter.raw_to_paragraphs(txt)

# Segment each paragraph to (list of sentences, list of spans)
sentences = segmenter.paragraphs_to_sentences(paragraphs)

# Get words with spans
words = segmenter.paragraphs_to_words(sentences)
        
# Detect smoothed dialogs
dialogs = segmenter.detect_dialog(p_types, tolerance=2)
starts = {start: i for i, (start,stop) in enumerate(dialogs)}      
stops = {stop: i for i, (start,stop) in enumerate(dialogs)}

# Define alternating colors for each type of paragraph
colors = {
    'dialog': ['background-color: #81F7BE', 'background-color: #81F7D8'],
    'normal': ['background-color: #A9D0F5', 'background-color: #A9BCF5'],
    'chapter': ['background-color: #FFFF66', 'background-color: #FFFF66'],
    'dialogStartStop': ['background-color: yellow;', 'background-color: yellow']
}
        
#%% 1. Export numbered paragraphs
rows = [prettify.content_comment_row('Number', 'Original text','Comments')]
for i,(p,p_type) in enumerate(zip(paragraphs, p_types)):
    style = colors[p_type][i%2]
    rows.append(prettify.content_comment_row(i, p, p_type, style=style))
    
table = prettify.table('\n'.join(rows))
html = prettify.html(table)
f_out = open('www/paragraphs.html','w')
f_out.write(html)
f_out.close()    
          
        
#%% 2. Export numbered paragraphs with dialog detection
rows = [prettify.content_comment_row('Number', 'Original text','Comments')]
for i,(p,p_type) in enumerate(zip(paragraphs, p_types)):
    if i in starts:
        rows.append(prettify.merged_row('Conversation {} -->'.format(starts[i]), 3, colors['dialogStartStop'][0]))
    if i in stops:
        rows.append(prettify.merged_row('<-- End {}'.format(stops[i]), 3, colors['dialogStartStop'][1]))
    style = colors[p_type][i%2]
    rows.append(prettify.content_comment_row(i, p, p_type, style=style))
    
table = prettify.table('\n'.join(rows))
html = prettify.html(table)
f_out = open('www/dialogs.html','w')
f_out.write(html)
f_out.close()    
   
#%% 3a. Export numbered paragraphs with dialog AND named entity detection
# Train Named Entity on whole text
print 'Learning all relevant characters'
ppl = PeopleClass(train_set=txt, min_count=3)
        
#%%
print 'Analyzing interactions'
in_conversation = False
rows = [prettify.content_comment_row('Number', 'Original text','Comments')]
interactions = np.zeros((ppl.num(), ppl.num()))
for i,(p,p_type) in enumerate(zip(paragraphs, p_types)):
    if (i+1)%10==0:
        print 'Processing paragraph {}/{}'.format(i+1, len(paragraphs))
    if i in starts: # start of conversation
        rows.append(prettify.merged_row('Conversation {} -->'.format(starts[i]), 3, colors['dialogStartStop'][0]))
        characters = set()
        in_conversation = True
    if in_conversation: # middle of conversation
        current_characters = ppl.predict(p)
        characters = characters.union(current_characters)
    if i in stops: # end of conversation
        rows.append(prettify.merged_row('<-- End {}'.format(stops[i]), 3, colors['dialogStartStop'][1]))
        rows.append(prettify.merged_row('Featured characters: {}'.format(', '.join(map(ppl.get,characters))), 3, colors['dialogStartStop'][1]))
        in_conversation = False
        # Update interactions
        for ch1 in characters:
            for ch2 in characters:
                if ch1!=ch2:
                    interactions[ch1,ch2] += 1
    style = colors[p_type][i%2]
    rows.append(prettify.content_comment_row(i, p, p_type, style=style))
    
table = prettify.table('\n'.join(rows))
html = prettify.html(table)
f_out = open('www/peopleA.html','w')
f_out.write(html)
f_out.close()               
        
#%% generate graph        
max_chars  = 20
edges = []
weights = []
node_weights = interactions.sum(axis=0)
# characters sorted by node weight
sorted_characters = sorted(np.arange(interactions.shape[0]), key=lambda i:node_weights[i], reverse=True)     
important_characters = sorted_characters[:min(max_chars, len(sorted_characters))]               
for i in range(interactions.shape[0]):
    for j in range(i+1, interactions.shape[0]):
        if i in important_characters and j in important_characters:
            if interactions[i,j]>0.5:
                edges.append((ppl.get(i), ppl.get(j)))
                weights.append(interactions[i,j])
weights = np.array(weights)
#draw_graph(edges, labels=weights, edge_size=weights)
graph_txt = draw_graphviz(edges, weights, smallest=4.)
graph_file = open('www/graph.gv','w') # important : use engine neato from GraphViz
graph_file.write(graph_txt)
graph_file.close()
   
       
#%%                   
'''
#%% (not working well) Export sentences with physical entities
# Get tags
tags = [[nltk.pos_tag(sent) for sent,span in paragraph] for paragraph in words]

#%% Filter Tags
vtags = [[[(word,tag) for word,tag in sent if tag in {'VBP','VBD','VB','VBN','VBG','MD','VBZ'}]
    for sent in paragraph] for paragraph in tags]
ntags = [[[(word,tag) for word,tag in sent if tag in {'NN','NNS'}]
    for sent in paragraph] for paragraph in tags]
  
rows = [prettify.content_comment_row('Original text','Comments')]
for i,(p,p_type,p_tag) in enumerate(zip(paragraphs, p_types, ntags)):
    style = colors[p_type][i%2]
    flat_tags = itertools.chain(*p_tag)
    flat_tags = '<br>'.join([word for word,tag in flat_tags])
    rows.append(prettify.content_comment_row(i, p, flat_tags, style=style))
    
table = prettify.table('\n'.join(rows))
html = prettify.html(table)
f_out = open('www/physics.html','w')
f_out.write(html)
f_out.close()
'''