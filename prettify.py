# -*- coding: utf-8 -*-
'''
@brief Tools for exporting augmented Novel
@date April 2015
@author Gabriel Huang
'''

import itertools

#####################################
# String manipulation
#####################################
html_body = u'''
<html>
<meta charset="utf-8"/>
<head>
<link rel="stylesheet" type="text/css" href="out.css">
<style>
td{{
    text-align: left;
}}
</style>
</head>
<body>
<div class="CSSTableGenerator" >
{content}
</div>
</body>
</html>
'''

def value_to_yellow(x):
    n = int(255*(1.-x))
    if n<0xf:
        hx = u'0'+hex(n)[2:]
    else:
        hx = hex(n)[2:]
    return u'#ffff'+hx

def value_to_size(x, min_sz=0.75, max_sz=2.):
    size = min_sz+x*(max_sz-min_sz)
    return str(int(100*size))+u'%'

def decorate_color(text, value):
    return u'<mark style="background-color: {color}">{text}</mark>\n'.format(
                text=text, color=value_to_yellow(value))

def decorate_color_and_size(text, value):
    return u'<mark style="font-size: {sz}; background-color: {color}">{text}</mark>\n'.format(
            text=text, color=value_to_yellow(value), sz=value_to_size(value))
 
def translate_newlines(txt):
    '''
    Transform newlines into <br>newlines
    '''
    lines = txt.split('\n')
    return u'<br>\n'.join(lines)    
    
#####################################
# Reshape utils
#####################################    
def combine_spans(sent_spans, word_spans):
    out = []
    for local_word_spans,(sent_start,sent_stop) in zip(word_spans, sent_spans):
        for word_start,word_stop in local_word_spans:
            out.append((sent_start+word_start, sent_start+word_stop))
    return out
    
def combine_scores(scores):
    '''Combines [[score]] into [score] per word'''
    return itertools.chain(*scores)

                               
#####################################
# Export HTML
#####################################          
                               
                            
def prettify(chunks, values, join='.'):
    '''
    Export chunks with values.
    This ignores the original formatting.
    '''
    doc = []
    for chunk,value in zip(chunks, values):
        doc.append(decorate_color_and_size(chunk, value))
    t = join.join(doc)
    return html_body.format(content=t)    
    
    
def prettify_sentences(chunks, values):
    '''
    Export sentences of words annotated
    by sentences of values.
    This ignores the original formatting.
    '''
    doc = []
    for chunk_sent,val_sent in zip(chunks, values):
        for chunk,value in zip(chunk_sent,val_sent):
            doc.append(decorate_color(chunk, value))
        doc.append(u'<br>')
    t = u' '.join(doc)
    return html_body.format(content=t)    


def prettify_in_place(text, spans, values):
    '''
    Annotate text
    Assumes that spans are monotonically increasing and non-overlapping
    This preserves the original formatting
    '''
    out = []
    last_end = 0
    for (begin, end),val in zip(spans, values):
        if begin>last_end:
            out.append(translate_newlines(text[last_end:begin]))
        out.append(decorate_color(translate_newlines(text[begin:end]), val))
        last_end = end
    out = u''.join(out)
    return html_body.format(content=out)
    
    
def content_comment_row(*args, **kwargs):
    '''
    Return a row in table
    
    Parameters:
    *args: one argument per cell
    **kwargs: style=(replace with css string)
    '''
    style = kwargs.get('style', '')    
    acc = [u'<tr>']    
    for arg in args:
        acc.append(u'<td class="content" style="{}">{}</td>'.format(style, arg))
    acc.append(u'</tr>')
    return u' '.join(acc)

    
def merged_row(text, cols, style=''):
    '''
    Return an empty, merged row
    
    Parameters:
    cols: number of columns
    style: css style string
    '''  
    acc = [u'<tr>']    
    acc.append(u'<td colspan="{}" class="content" style="{}">{}</td>'.format(cols, style, text))
    acc.append(u'</tr>')
    return u' '.join(acc)
    
    
def table(rows):
    '''
    Return a table with html content
    '''    
    return u'<table>\n{}\n</table>'.format(rows)
    
    
def html(body_content):
    '''
    Return a html with given body content
    '''    
    return html_body.format(content=body_content)