# -*- coding: utf-8 -*-
"""
Created on Thu May 07 10:52:57 2015

@author: gabi
"""

import nltk
import re
import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from nltk.corpus import wordnet as wn


titles = set(('Mr.','Mrs.','Ms.','Monsieur','Madame','Mister','Madam','Miss','Dr.','Doctor'))
male_names = open('data/dist.male.first.txt').read().lower().split()[::4]
female_names = open('data/dist.female.first.txt').read().lower().split()[::4]
last_names = open('data/dist.all.last.txt').read().lower().split()[::4]
person_synset = wn.synset('person.n.01')


def is_person_wordnet(word):
    '''
    Returns if WordNet knows a person named 'word'
    Rules:
    1) If not synset corresponds, it's a person
    2) If synsets are found but don't contain nouns, it's not a person
    3) If synsets are found but all noun synsets are instances it's a person
    4) If at least one of the synsets inherits from person.n.01 then it's a person
    '''
    synsets = wn.synsets(word)
    if not synsets: # Rule 1
        return True
    if all(synset.pos()!='n' for synset in synsets): # Rule 2
        return False
    # At this point there is at least one noun
    instances = []
    for synset in synsets:
        if synset.pos() == 'n':
            hyper = set([i for i in synset.closure(lambda s:s.hypernyms())])
            if person_synset in hyper: # Rule 4
                return True
            instances.append(not hyper)
    return all(instances) # Rule 3


def is_person_census(word):
    '''
    True if word is in the census name list
    '''    
    return (word in male_names) or (word in female_names) or (word in last_names)    
    
    
def is_person(words):
    '''
    Combines is_person_wordnet and is_person_census to tell is someone is a person
    '''
    if len(words)>1 and words[0] in titles:
        return True
    return all(is_person_census(word.lower()) or is_person_wordnet(word.lower()) for word in words)


def extract_ne(txt):
    '''
    Extract named entities using NLTK chunker
    '''
    words = nltk.word_tokenize(txt)
    tags = nltk.pos_tag(words)
    ne = nltk.ne_chunk(tags)
    ne = [trees for trees in ne if isinstance(trees, nltk.Tree) and trees.label()=='PERSON']
    return ne


def accumulate_ch(named_entities):
    '''
    Returns unfiltered list of characters (might be redundant)
    '''
    characters = {}
    for entity in named_entities:
        # accumulate
        parts = [word for word,tag in entity.leaves()]
        key = ' '.join(parts)
        count = characters[key][1] if key in characters else 0
        characters[key] = (parts, count+1) 
    return characters


def filter_ch(characters):
    '''
    filter non-people named entities
    '''
    characters = {key:(parts,count) for key,(parts,count) in characters.items() if is_person(parts)}
    return characters


def merge_ch(characters):
    '''
    Merge characters.
    
    Each named entity is a vertex in a graph.
    Two vertices are connected if they have at least one word in common
    Each character is then DEEFINED as a connected component
    This might merge together people with the same first or last name
    and require some postprocessing
    '''    
    graph =  csr_matrix((len(characters), len(characters)), dtype=bool) #np.zeros((len(characters), len(characters)))
    for i,(_,(ch_i,_)) in enumerate(characters.items()):
        for j,(_,(ch_j,_)) in enumerate(characters.items()[:i]):
            if set(ch_i).difference(titles).intersection(set(ch_j)):
                graph[i,j] = graph[j,i] = True
    num_comp, labels = connected_components(graph, directed=False)
    synsets = [[] for i in range(num_comp)]
    return synsets

#%% Test
if __name__=='__main__':
    txt = open('data/gatsby.txt').read()[10000:60000]
    
    named_entities = extract_ne(txt)
    ch1 = accumulate_ch(named_entities)
    ch2 = filter_ch(ch1)
    final_characters = merge_ch(ch2)
    print final_characters
