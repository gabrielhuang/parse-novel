# -*- coding: utf-8 -*-
'''
@brief Functions to cut text into paragraphs, sentences and words
@date April 2015
@author Gabriel Huang
'''

import nltk
from nltk.tokenize.punkt import PunktWordTokenizer
import re

empty_line = re.compile(r'[\t\ ]*\n[\t\ ]*[\n]+[\t\ ]*')
chapter = re.compile(r'(Chapter|CHAPTER|chapter)[\t\ ]+\d+')
tokenizer = PunktWordTokenizer()
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

def raw_to_paragraphs(txt):
    '''
    Divides text into a list of paragraphs or dialogues  
    
    Returns:
    list of (paragraphs, ptype)
    
    where ptype == 'dialog' or 'normal'
    '''
    paragraphs = empty_line.split(txt)
    ptypes = []
    for p in paragraphs:
        if p and p[0]=='"':
            ptypes.append('dialog')
        elif chapter.match(p):
            ptypes.append('chapter')
        else:
            ptypes.append('normal')
    return paragraphs, ptypes


def raw_to_sentences(txt):
    '''
    Divides a text into sentences
    
    Returns:
    (list of sentences, list of spans)
    '''
    sents = sent_detector.tokenize(txt)
    sent_spans = sent_detector.span_tokenize(txt)    
    return sents, sent_spans


def paragraphs_to_sentences(paragraphs):
    '''
    Divides a list of paragraphs into sentences
    
    Returns:
    (list of sentences, list of spans)
    '''

    acc = []
    for p in paragraphs:
        acc.append(raw_to_sentences(p))
    return acc


def raw_to_words(txt):
    '''
    Divides a text into words
    
    Returns:
    (list of words, list of spans)
    '''
    words = tokenizer.tokenize(txt)
    word_spans = tokenizer.span_tokenize(txt)
    return words, word_spans
    
    
def sentences_to_words(sentences):
    '''
    Divides a list of sentences into a list of (list of words, list of word_spans)
    '''
    return [raw_to_words(sent) for sent in sentences]


def paragraphs_to_words(paragraphs):
    '''
    Segments pre-segmented paragraphs into words
    '''
    acc = []
    for sents,_ in paragraphs:
        acc.append(sentences_to_words(sents))
    return acc
            
    
def detect_dialog(ptypes, tolerance=2):
    '''
    Detect continuous chunks of dialogues,
    tolerating gaps of size<=tolerance
    
    Returns:
    list of (begin, end) where begin is included and end is excluded
    '''
    # Get conversations
    conversations = []
    begin = 0
    while begin<len(ptypes):
        if ptypes[begin] == 'dialog':
            end = begin
            while end<len(ptypes) and ptypes[end] == 'dialog':
                end += 1
            conversations.append((begin, end))
            begin = end
        else:
            begin += 1
    # Smooth
    smoothed = []
    for i, current in enumerate(conversations):
        if smoothed and current[0]-smoothed[-1][1]<tolerance:
            smoothed[-1] = (smoothed[-1][0], current[1])
        else:
            smoothed.append(current)
    return smoothed
        
    
#########################
# Test
#########################    
if __name__=='__main__':
    test_txt = '''
    Chapter 1
    
    "Hi", said Tom.
    
    "What's up?", replied his best friend.
    
    A few seconds pass.    
    
    "We're darn high man!"
    
    They stared at
    each other, and laughed.
    They loved chilling
    on the hotel rooftop.
    '''
    print 'Test paragraphs'
    paragraphs, ptypes = raw_to_paragraphs(test_txt)
    print zip(ptypes, paragraphs)        
        
    print 'Test sentences'
    sentences = paragraphs_to_sentences(paragraphs)
    print sentences
    
    print 'Test words'
    words = paragraphs_to_words(sentences)
    print words
    
    print 'Detect Dialog'
    dialogs = detect_dialog(ptypes)
    print dialogs