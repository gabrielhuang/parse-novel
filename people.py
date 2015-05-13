# -*- coding: utf-8 -*-
'''
@brief Detect named entities in book
@author: Gabriel Huang

This uses two techniques. NLTK's named_entity (very slow and reliable)
or a simpler heuristic based on Capitalized words (fast and less reliable)
'''

import time
import sys
import nltk
import re
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from nltk.corpus import wordnet as wn


titles = set(('Mr.','Mrs.','Ms.','Monsieur','Madame','Mister','Madam','Miss','Dr.','Doctor',
             'Professor','Lord'))
male_names = open('data/dist.male.first.txt').read().lower().split()[::4]
female_names = open('data/dist.female.first.txt').read().lower().split()[::4]
last_names = open('data/dist.all.last.txt').read().lower().split()[::4]
person_synset = wn.synset('person.n.01')
object_synset = wn.synset('object.n.01') # includes location
# read stopwords
stopwords_file = open('data/stopwords.csv')
stopwords_file.readline() # read header
stopwords = stopwords_file.read().split()
stopwords_file.close()


def get_gender(name):
    is_male = name in male_names
    is_female = name in female_names
    if is_male and not is_female:
        return 'male'
    elif is_female and not is_male:
        return 'female'
    else:
        return 'neutral'
    

def all_noun_hypernyms(word):
    '''
    Return all noun hypernyms of word using wordnet
    '''
    synsets = wn.synsets(word)
    hyper = set()
    for synset in synsets:
        if synset.pos() == 'n':
            hyper = hyper | set([i for i in synset.closure(lambda s:s.hypernyms()+s.instance_hypernyms())])
    return hyper
    
    
def is_person_wordnet(word):
    '''
    Returns if WordNet knows a person named 'word'
    Rules (by precedence):
    1) If no synset corresponds, it's a person
    2) If synsets are found but don't contain nouns, it's not a person
    3) If at least one of the synsets inherits from a location then it's not a person
    4) If at least one of the synsets inherits from person.n.01 then it's a person    
    '''
    synsets = wn.synsets(word)
    if not synsets: # Rule 1
        return True
    if all(synset.pos()!='n' for synset in synsets): # Rule 2
        return False
    # At this point there is at least one noun
    hyper = all_noun_hypernyms(word)
    if object_synset in hyper: # Rule 3
        return False
    if person_synset in hyper: # Rule 4
        return True
    return False


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
    return all(word.lower() not in stopwords for word in words) and \
        all(is_person_census(word.lower()) or is_person_wordnet(word.lower()) for word in words)


def extract(txt):
    '''
    Step 1. Extract named entities using NLTK chunker
    '''
    words = nltk.word_tokenize(txt)
    tags = nltk.pos_tag(words)
    ne = nltk.ne_chunk(tags)
    ne = [trees for trees in ne if isinstance(trees, nltk.Tree) and trees.label()=='PERSON']
    return ne


#Punctuation that capitalizes the next word
shift_punct = set(('.','!','?'))
is_uppercase = re.compile(r'[A-Z]+')

def extract_no_postag(txt, ignore_after_punct=False):
    '''
    Alternative Step 1.
    Same as extract without POS tagging
    
    Parameters
    :ignore_after_punct: if true then ignore capitalized words after punctuation
    
    Returns
    list of names instead of nltk trees
    '''
    words = nltk.word_tokenize(txt)
    names = []
    previous = None
    for i, word in enumerate(words):
        if not ignore_after_punct or (i==0)\
        or( words[i-1] not in shift_punct) or word in titles:
            if word and is_uppercase.match(word[0]):
                word = word[0] + word[1:].lower() # change WILSON to Wilson
                if previous is not None and previous==i-1:                
                    names[-1] += ' ' + word
                else:
                    names.append(word)
                previous = i
    return names


def destructure(named_entity):
    parts = [word for word,tag in named_entity.leaves()]
    key = ' '.join(parts)
    return key, parts


def destructure_no_postag(named_entity):
    parts = named_entity.split()
    key = named_entity
    return key, parts
    

def remove_duplicates(named_entities, destructure=destructure):
    '''
    Step 2. Remove duplicates and return unfiltered list of characters (might be redundant)
    '''
    characters = {}
    for entity in named_entities:
        # accumulate
        key, parts = destructure(entity)
        count = characters[key][1] if key in characters else 0
        characters[key] = (parts, count+1) 
    return characters


def filter_persons(characters, min_count=1):
    '''
    Step 3. filter out non-people named entities
    '''
    characters = {key:(parts,count) for key,(parts,count) in characters.items()\
        if is_person(parts) and count>=min_count}
    return characters


"""
def persons_to_groups(characters):
    '''
    Step 4.a Merge characters: all named entities sharing one or more tokens are merged
    
    Returns:
    a list of synsets
    a synset = [[('Tom',{'Tom'}),('Tom Buchanan',{'Tom',Buchanan'})], count, title]
    where count is the number of occurences of synset
    and title is the label of the synset
    
    Each named entity is a vertex in a graph.
    Two vertices are connected if they have at least one word in common
    Each character is then DEEFINED as a connected component
    This might merge together people with the same first or last name
    and require some postprocessing (see split_ch)
    '''    
    graph =  csr_matrix((len(characters), len(characters)), dtype=bool) #np.zeros((len(characters), len(characters)))
    for i,(_,(ch_i,_)) in enumerate(characters.items()):
        for j,(_,(ch_j,_)) in enumerate(characters.items()[:i]):
            if set(ch_i).difference(titles).intersection(set(ch_j)):
                graph[i,j] = graph[j,i] = True
    num_comp, labels = connected_components(graph, directed=False)
    synsets = [[] for i in range(num_comp)]
    for i,(key,(tokens,count)) in enumerate(characters.items()):
        synsets[labels[i]].append((key, [token for token in tokens if token not in titles], count)) # never keep titles
    return synsets
"""


def strip_titles(parts):
    return [part for part in parts if part not in titles]
    
    
def persons_to_groups(persons):
    '''
    Step 4.b Split character synset:
    
    1) For each synset find unambiguous instances
    of the form "First_Name Last_Name" or "Title First_Name Last_Name"
    and create a new synset for each of them or merge similar ones
    2) For each remaining (ambiguous) instance assign them to all synsets 
    with common tokens
    3) Instances not assigned anywhere are given their own synset
    4) Accumulate counts and generate title
    '''

    equiv_synsets = [] # will be equivalent to the actual groups_to_synsets
    # Step 1)
    for key, (parts, count) in persons.items():
        equiv_synset = None
        parts = strip_titles(parts) 
        if len(parts)==2:
            for s in equiv_synsets:
                if any((set(parts)==set(other_parts) for _,other_parts,_ in s)):
                    equiv_synset = s
                    break
            if equiv_synset is None:
                equiv_synsets.append([[key, parts, count]])
            else:
                equiv_synset.append([key, parts, count])
    # Step 2 & 3)
    for key, (parts, count) in persons.items():
        matched_unambiguous = False
        parts = strip_titles(parts)
        if len(parts)!=2:
            for s in equiv_synsets:
                if any((set(parts).issubset(other_parts) for _,other_parts,_ in s)):
                    s.append([key, parts, count]) # Step 2
                    matched_unambiguous = True
            if not matched_unambiguous: # Step 3        
                equiv_synsets.append([[key, parts, count]])
    return equiv_synsets
    
    
def groups_to_synsets(synsets, use_first=True):
    '''
    Step 4.c Generate labels and total counts for each synset
    '''
    new_synsets = []
    for synset in synsets:
        counts = 0
        best_label = ''
        for key, parts, count in synset:
            counts += count
            if len(key)>len(best_label): # pick longest one to represent
                best_label = key
        if use_first:
            best_label = synset[0][0]
        new_synsets.append(([(key,parts) for key,parts,count in synset], counts, best_label))
    return sorted(new_synsets, key=lambda (a,b,c):b, reverse=True)
    

def detect_persons(txt, final_characters, ordering=None, extract=extract, destructure=destructure, verbose=False):
    '''
    Step 5. (Prediction) Given trained final characters, detect them in a given (new) paragraph
    It also flips final_characters to account for recency
    '''
    if ordering is None:
        ordering = [i for i in range(len(final_characters))] # default order
    ne = extract(txt)
    results = []
    for named_entity in ne:
        best_synset = None
        key,parts= destructure(named_entity)
        parts = set(strip_titles(parts))
        # Search in final_characters
        for i, j in enumerate(ordering):
            synset, count, label = final_characters[j]
            for ref_key, ref_part in synset:
                if parts.intersection(ref_part):
                    best_synset = i, j # index in ordering, index in final_characters
                    break
            if best_synset is not None:
                results.append(best_synset[1])
                # Bring this result to front
                # these two are O(n) in number of characters, totally acceptable
                del ordering[best_synset[0]]
                ordering = [best_synset[1]] + ordering
                break
        if verbose:
            print '{} --> {}'.format(key, final_characters[best_synset[1]][2] if best_synset is not None else 'IGNORED')
    return results, ordering
    

class People:
    def __init__(self, train_set=None, *args, **kwargs):
        '''
        This is like People but uses a simple and fast caps-based heuristic        
        instead of part of speech tagging.
        Will train model if train_set is not None
        '''
        if train_set is not None:
            self.train(train_set, *args, **kwargs)
    def train(self, text, use_postag=False, min_count=1):
        if use_postag:
            named_entities = extract(text)
            ch1 = remove_duplicates(named_entities)
        else:
            named_entities = extract_no_postag(text, ignore_after_punct=True)
            ch1 = remove_duplicates(named_entities, destructure=destructure_no_postag)
        ch2 = filter_persons(ch1, min_count)
        ch3 = persons_to_groups(ch2)
        self.final_characters= groups_to_synsets(ch3) 
        self.reset_recency()
    def predict(self, text, **kwargs):
        detected_ch, self.ordering = detect_persons(text, self.final_characters, ordering=self.ordering,
                                extract=extract_no_postag, destructure=destructure_no_postag, **kwargs)
        return detected_ch
    def reset_recency(self):
        self.ordering = None
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
    text2 = open('data/hp.txt').read()[10000:20000] 
    text1 = 'Ginny also known as Ginny Potter says hi to Harry. '+\
    'But Mr. Potter is not happy because of Ginny. Mrs. Potter is happy though.'    
    
    
    #%%
    for txt in [text1, text2]:
        for use_postag in [False, True]:
            last_time = t = time.time()
            print '\nUse postag {}'.format(use_postag)
            print 'Training Characters'
            ppl = People(txt, use_postag=use_postag)
            print 'Found \n{}\n'.format(ppl.final_characters)
            
            #%%
            print 'Detecting Characters'
            
            detected_ch = ppl.predict(txt, verbose=False)
            characters = map(ppl.get, detected_ch)
            if len(characters)>20:
                characters = set(characters)
            print characters
            print 'Total time {} seconds'.format(time.time() - last_time)
            sys.stdout.flush()
        