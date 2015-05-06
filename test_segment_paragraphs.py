# -*- coding: utf-8 -*-
'''
@brief Test application to export augmented novel
@date April 2015
@author Gabriel Huang
'''

import nltk
import segmenter
import prettify
import itertools
import NamedEntityIdentifier
reload(segmenter)
reload(prettify)
reload(NamedEntityIdentifier)
from NamedEntityIdentifier import NamedEntityIdentifier


# Load text
#txt_file = open('sherlock-pg1661.txt','r')
txt_file = open('gatsby.txt','r')
txt = txt_file.read(100000).strip()[3000:]


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
f_out = open('paragraphs.html','w')
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
f_out = open('dialogs.html','w')
f_out.write(html)
f_out.close()    
   
        
#%% 3. Export numbered paragraphs with dialog AND named entity detection
# Train Named Entity on whole text
nei = NamedEntityIdentifier()
nei.train(txt)        
        
in_conversation = False
rows = [prettify.content_comment_row('Number', 'Original text','Comments')]
for i,(p,p_type) in enumerate(zip(paragraphs, p_types)):
    if i in starts: # start of conversation
        rows.append(prettify.merged_row('Conversation {} -->'.format(starts[i]), 3, colors['dialogStartStop'][0]))
        characters = set()
        in_conversation = True
    if in_conversation: # middle of conversation
        current_characters = set(name for pos,name in nei.predict(p))
        characters = characters.union(current_characters)
    if i in stops: # end of conversation
        rows.append(prettify.merged_row('<-- End {}'.format(stops[i]), 3, colors['dialogStartStop'][1]))
        rows.append(prettify.merged_row('Featured characters: {}'.format(', '.join(characters)), 3, colors['dialogStartStop'][1]))
        characters = set()
        in_conversation = True
    style = colors[p_type][i%2]
    rows.append(prettify.content_comment_row(i, p, p_type, style=style))
    
table = prettify.table('\n'.join(rows))
html = prettify.html(table)
f_out = open('people.html','w')
f_out.write(html)
f_out.close()             
                          
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
f_out = open('physics.html','w')
f_out.write(html)
f_out.close()