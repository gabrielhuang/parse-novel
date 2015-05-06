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

reload(segmenter)
reload(prettify)

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
        
#%% Export paragraphs
rows = [prettify.content_comment_row('Original text','Comments')]
for i,(p,p_type) in enumerate(zip(paragraphs, p_types)):
    if p_type == 'dialog':
        style = 'background-color: #81F7BE' if i%2 else 'background-color: #81F7D8'
    else:
        style = 'background-color: #A9D0F5' if i%2 else 'background-color: #A9BCF5'
    rows.append(prettify.content_comment_row(p, p_type, style, style))
    
table = prettify.table('\n'.join(rows))
html = prettify.html(table)
f_out = open('out.html','w')
f_out.write(html)
f_out.close()    
        
#%% Export sentences with verbs highlighted
# Get tags
tags = [[nltk.pos_tag(sent) for sent,span in paragraph] for paragraph in words]

#%% Filter Tags
vtags = [[[(word,tag) for word,tag in sent if tag in {'VBP','VBD','VB','VBN','VBG','MD','VBZ'}]
    for sent in paragraph] for paragraph in tags]
ntags = [[[(word,tag) for word,tag in sent if tag in {'NN','NNS'}]
    for sent in paragraph] for paragraph in tags]
  
rows = [prettify.content_comment_row('Original text','Comments')]
for i,(p,p_type,p_tag) in enumerate(zip(paragraphs, p_types, ntags)):
    if p_type == 'dialog':
        style = 'background-color: #81F7BE' if i%2 else 'background-color: #81F7D8'
    else:
        style = 'background-color: #A9D0F5' if i%2 else 'background-color: #A9BCF5'
    flat_tags = itertools.chain(*p_tag)
    flat_tags = '<br>'.join([word for word,tag in flat_tags])
    rows.append(prettify.content_comment_row(p, flat_tags, style, style))
    
table = prettify.table('\n'.join(rows))
html = prettify.html(table)
f_out = open('out.html','w')
f_out.write(html)
f_out.close()