import nltk
from nltk.tokenize.punkt import PunktWordTokenizer
import re

empty_line = re.compile(r'[\t\ ]*\n[\t\ ]*[\n]+[\t\ ]*')
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
            
    
#########################
# Test
#########################    
if __name__=='__main__':
    test_txt = '''
    Chapter 1
    
    "Hi", said Tom.
    
    "What's up?", replied his best friend.
    
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