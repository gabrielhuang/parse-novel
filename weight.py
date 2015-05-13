# -*- coding: utf-8 -*-
'''
@brief: tf.stf.idf.isf weighing scheme
@author: Gabriel Huang
@date: May 2015

Weighing scheme from Mihalcea & Ceylan "Explorations in Automatic Book Summarization"
where:
tf number of times word in book
idf number of times word in external corpus
stf number of times word in segment
isf number of segments containing word
'''

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.datasets import fetch_20newsgroups
import numpy as np
import prettify
import segmenter

#%%

class Weighter:
    '''
    This class uses a tf.idf.stf.isf weighing scheme
    '''
    def train(self, segments, ignore_before=4, ignore_after=4):
        '''
        This uses the 20newsgroups dataset for idf
        
        Parameters:
        :segments: list of strings where each string is a segment
        '''        
        data = fetch_20newsgroups(subset='train').data
        stripped_data = []
        
        for d in data:
            lines = d.split('\n')
            if len(lines)>ignore_before+ignore_after:
                stripped_data.append('\n'.join(lines[ignore_before:-ignore_after]))
        
        txt = ''.join(segments)
        stripped_data.append(txt)
        
        # Train corpus tf-idf
        tfidf_corpus = TfidfVectorizer(stop_words='english')
        tfidf_corpus.fit(stripped_data)
        book_scores = tfidf_corpus.transform([txt])
        print 'Learned {} features CORPUS'.format(len(tfidf_corpus.get_feature_names()))
        
        # Train document segment-wise tf-idf 
        tfidf_book = TfidfVectorizer(vocabulary=tfidf_corpus.vocabulary_)
        segment_scores = tfidf_book.fit_transform(segments)
        print 'Learned {} features BOOK'.format(len(tfidf_book.get_feature_names()))

        # Now get word scores in each segment
        final_scores = book_scores.multiply(segment_scores)

        idx_to_word = tfidf_corpus.get_feature_names()
        word_scores = []
        for i, segment_scores in enumerate(final_scores):
            scores = {}
            for j in segment_scores.indices:        
                scores[idx_to_word[j]] = segment_scores[0, j]
            word_scores.append(scores)
            
        self.word_scores = word_scores
        self.analyze = tfidf_corpus.build_analyzer()
    def predict(self, text, segment_idx, smoothing=1):
        '''
        Compute un_normalized score for text given segment number
        
        Parameters:
        :smoothing: longer sentences are penalized by a factor 1/np.log(smoothing+len(words))
        '''
        words = self.analyze(text)        
        return sum(self.word_scores[segment_idx].get(word, 0.) for word in words)/np.log(1+smoothing+len(words))
    def predict_all(self, segments, **kwargs):
        '''
        Compute unnormalized score for segment text
        
        Parameters:
        :segments: list of list of strings 
        '''
        scores = []
        for i, segment in enumerate(segments):
            for sentence in segment:
                score = self.predict(sentence, i, **kwargs)
                scores.append(score)
        return scores

#%% Test
if __name__=='__main__': 
    txt = open('data/gatsby.txt').read()
    num_segments = 5
    size_segments = len(txt)/num_segments
    segments = [txt[i*size_segments:(i+1)*size_segments] for i in range(num_segments)]
        
    weighter = Weighter()
    weighter.train(segments)
    
    spans = []
    values = []
    seen_chars = 0
    for segment_idx, segment in enumerate(segments):
        sentences, current_spans  = segmenter.raw_to_sentences(segment)
        current_spans = np.array(current_spans) + seen_chars
        for sentence, span in zip(sentences, current_spans):
            score = weighter.predict(sentence, segment_idx)
            values.append(score)
            spans.append(span)
        seen_chars += len(segment)            
                
    values = 10. * np.array(values)
    html = prettify.prettify_in_place(txt, spans, values)
    f_out = open('www/scores.html','w')
    f_out.write(html)
    f_out.close()   
