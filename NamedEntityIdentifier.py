'''
Created on May 4, 2015

@author: billyanhuang
'''
import STok #works better than the nltk one
import NEName #class for character names and comparisons
import LinkedList #recency-based coreference
from nltk.tokenize import word_tokenize
from nltk.chunk import ne_chunk

#name stuffs
titles = set(["Mr.", "Mrs.", "Ms.", "Miss", "Mister", "Dr.", "Doctor", "Monsieur", "Madame"]) #titles
suffixes = set(["Jr.", "Sr."]) #suffixes
notperson = set(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
                 "East", "West", "North", "South",
                 "Street", "Road", "Avenue",
                 "York", "Chicago", "Los", "San", "Oxford",
                 "Island", "Coast", "Bay", "Sound",
                 "The", "A", "An", "That", "There", "This", "Thus", "How", "Where", "When", "Why", "Who",
                 "Father", "Mother", "His", "Her", "He", "She", "It", "Its", "You", "I",
                 "Not", "Never", "And", "Or", "But", "Then", "After", "Before",
                 "Some", "Many", "Few", "In", "To",
                 "God",
                 "My", "Hers", "Our", "We", "Oh", "They",
                 "Yes", "No", "Now", "What",
                 "Is", "As"]) #can add a lot more - stopwords, dates, proper nouns, etc.
#will probably thoroughly make a set later

def type(ent):
    for part in ent:
        if part in notperson:
            return False
    return True
        
def extractNE(text):
    names = LinkedList.LinkedList()
    sentencestarters = set([])
    for sent in STok.stok(text):
        tok = word_tokenize(sent)
        tent = []
        if len(tok) > 0 and tok[0] in sentencestarters: #first word of sentence - tricky source of error
            tent.append(tok[0])
        for i in range(1, len(tok)):
            if STok.isuc(tok[i][0]) and (tok[i] != "I"): #appending terms to named entity
                tent.append(tok[i])
            else:
                if len(tent) > 0 and type(tent): #will add if the named entity 
                    matchNE(names, tent)
                    tent = []
    return names

def matchNE(names, ent):
    curnode = names.head
    match = False
    tname = NEName.Name(ent)
    if (tname): #is a name
        while (not match) and (curnode): #matching with older names in order of recency
            match = curnode.data.match(tname)
            if match: #refreshes node it is matched with
                names.refresh(curnode)
            curnode = curnode.nextNode
        if not match: #adds node
            names.append(LinkedList.Node(tname))
    
###################################################################################################

def get_all_ne(text):
    NEs = {} #final named entities
    name = extractNE(text).head
    while (name): #iterating over all named entities
        info = name.data.printout()
        NEs[info[0]] = info[1]
        name = name.nextNode
    sNEs = sorted(NEs.iteritems(),key=lambda (k,v): v,reverse=True) #sorted by count
    return sNEs
    
if __name__=='__main__':
    text = open("text.txt", "r").read()
    sNEs = get_all_ne(text)
    for name in sNEs: #output
        print name