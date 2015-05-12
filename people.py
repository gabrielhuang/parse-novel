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


titles = set(('Mr.','Mrs.','Ms.','Monsieur','Madame','Mister','Madam','Miss','Dr.','Doctor'))
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
    hyper = set()
    for synset in synsets:
        if synset.pos() == 'n':
            hyper = hyper | set([i for i in synset.closure(lambda s:s.hypernyms()+s.instance_hypernyms())])
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


def extract_ne(txt):
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
    Same as extract_ne without POS tagging
    
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
                if previous is not None and previous==i-1:                
                    names[-1] += ' ' + word
                else:
                    names.append(word)
                previous = i
    return names


def destructure_ne(named_entity):
    parts = [word for word,tag in named_entity.leaves()]
    key = ' '.join(parts)
    return key, parts


def destructure_no_postag(named_entity):
    parts = named_entity.split()
    key = named_entity
    return key, parts
    

def accumulate_ch(named_entities, destructure_ne=destructure_ne):
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


def detect_ch(txt, final_characters, extract_ne=extract_ne, destructure_ne=destructure_ne, verbose=False):
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
    def predict(self, text, **kwargs):
        detected_ch = detect_ch(text, self.final_characters, **kwargs)
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


class PeopleNoPos(People):
    def __init__(self, train_set=None, **kwargs):
        '''
        This is like People but uses a simple and fast caps-based heuristic        
        instead of part of speech tagging.
        Will train model if train_set is not None
        '''
        People.__init__(self, train_set, **kwargs)
    def train(self, text, min_count=1):
        named_entities = extract_no_postag(text, ignore_after_punct=True)
        ch1 = accumulate_ch(named_entities, destructure_ne=destructure_no_postag)
        ch2 = filter_ch(ch1, min_count=min_count)
        self.final_characters = merge_ch(ch2)
    def predict(self, text, **kwargs):
        detected_ch = detect_ch(text, self.final_characters, 
                                extract_ne=extract_no_postag, destructure_ne=destructure_no_postag, **kwargs)
        return detected_ch
      
        
        
#%% Test
if __name__=='__main__':
    txt = open('data/gatsby.txt').read()[10000:40000]
    txt2 = open('data/gatsby.txt').read()[50000:80000]
    
    for name, PeopleType in [('PeopleNoPos',PeopleNoPos), ('People',People)]:
        last_time = t = time.time()
        print '\nModel name {}'.format(name)
        print 'Training Characters'
        ppl = PeopleType(txt)
        print 'Found \n{}\n'.format(ppl.final_characters)
        
        #%%
        print 'Detecting Characters'
        
        detected_ch = ppl.predict(txt2, verbose=False)
        characters = map(ppl.get, detected_ch)
        print characters
        print 'Total time {} seconds'.format(time.time() - last_time)
        sys.stdout.flush()