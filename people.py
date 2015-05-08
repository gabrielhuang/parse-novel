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
    Step 1. Extract named entities using NLTK chunker
    '''
    words = nltk.word_tokenize(txt)
    tags = nltk.pos_tag(words)
    ne = nltk.ne_chunk(tags)
    ne = [trees for trees in ne if isinstance(trees, nltk.Tree) and trees.label()=='PERSON']
    return ne


def destructure_ne(named_entity):
    parts = [word for word,tag in named_entity.leaves()]
    key = ' '.join(parts)
    return key, parts


def accumulate_ch(named_entities):
    '''
    Step 2. Remove duplicates and return unfiltered list of characters (might be redundant)
    '''
    characters = {}
    for entity in named_entities:
        # accumulate
        key, parts = destructure_ne(entity)
        count = characters[key][1] if key in characters else 0
        characters[key] = (parts, count+1) 
    return characters


def filter_ch(characters, min_count=1):
    '''
    Step 3. filter out non-people named entities
    '''
    characters = {key:(parts,count) for key,(parts,count) in characters.items()\
        if is_person(parts) and count>=min_count}
    return characters


def merge_ch(characters):
    '''
    Step 4. Merge characters. (Into character synsets)
    
    Returns:
    a list of synsets
    a synset = [[('Tom',{'Tom'}),('Tom Buchanan',{'Tom',Buchanan'})], count, title]
    where count is the number of occurences of synset
    and title is the label of the synset
    
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
    synsets = [[[],0,''] for i in range(num_comp)]
    for i,(key,(tokens,count)) in enumerate(characters.items()):
        synsets[labels[i]][0].append((key, set(tokens).difference(titles))) # never keep titles
        synsets[labels[i]][1] += 1
        if len(key)>len(synsets[labels[i]][2]): # pick longest one to represent
            synsets[labels[i]][2] = key
    synsets = sorted(synsets, key = lambda (instance,count,title):count, reverse = True)
    return synsets


def detect_ch(txt, final_characters, verbose=False):
    '''
    Step 5. (Prediction) Given trained final characters, detect them in a given (new) paragraph
    '''
    ne = extract_ne(txt)
    results = set()
    for named_entity in ne:
        best_synset = None
        key,parts= destructure_ne(named_entity)
        parts = set(parts)
        # Search in final_characters
        for i, (synset, count, label) in enumerate(final_characters):
            for ref_key, ref_part in synset:
                if parts.intersection(ref_part):
                    best_synset = i
                    break
            if best_synset is not None:
                break
        if best_synset is not None:
            results.add(best_synset)
        if verbose:
            print '{} --> {}'.format(key, final_characters[best_synset][2] if best_synset is not None else 'IGNORED')
    return results
    
    
class People:
    def __init__(self, train_set=None, **kwargs):
        '''
        Will train model if train_set is not None
        '''
        if train_set is not None:
            self.train(train_set, **kwargs)
    def train(self, text, min_count=1):
        named_entities = extract_ne(text)
        ch1 = accumulate_ch(named_entities)
        ch2 = filter_ch(ch1, min_count=min_count)
        self.final_characters = merge_ch(ch2)
    def predict(self, text):
        detected_ch = detect_ch(text, self.final_characters)
        return detected_ch
    def get(self, index):
        '''
        Returns label of synset corresponding to index
        '''        
        return self.final_characters[index][2]
    def num(self):
        '''
        Return number of persons learned during training
        '''
        return len(self.final_characters)
        
#%% Test
if __name__=='__main__':
    txt = open('data/gatsby.txt').read()[10000:20000]
    
    print '\n\nTraining Characters'
    named_entities = extract_ne(txt)
    ch1 = accumulate_ch(named_entities)
    ch2 = filter_ch(ch1)
    final_characters = merge_ch(ch2)
    print final_characters

    #%%
    print '\n\nDetecting Characters'
    txt2 = open('data/gatsby.txt').read()[20000:30000]
    detected_ch = detect_ch(txt2, final_characters, verbose=True)
    print detected_ch