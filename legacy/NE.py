'''
Created on May 7, 2015

@author: billyanhuang
'''
import STok #works better than the nltk one
import NEName #class for character names and comparisons
import LinkedList #recency-based coreference
from nltk.tokenize import word_tokenize
from nltk import defaultdict
import math

titles = set(["Mr.", "Mrs.", "Ms.", "Miss", "Mister", "Dr.", "Doctor", "Monsieur", "Madame", "Monseigneur", "Sir", "Lady", "M.", "Mme.", "Mademoiselle"]) #titles
suffixes = set(["Jr.", "Sr."]) #suffixes

notperson = set(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
                 "East", "West", "North", "South",
                 "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", 
                 "Street", "Road", "Avenue",
                 "York", "Chicago", "Los", "San", "Oxford", "Paris",
                 "America", "American", "France", "French", "English", "England",
                 "Project", "Chapter",
                 "Island", "Coast", "Bay", "Sound",
                 "Oh", "Yeah", "Aw", "Aww", "Ohh", "O", "Mr", "Mrs",
                 "Original",
                 "Yes", "No", "God", "Please"]) #common sentence starters
articles = set(["the", "The", "a", "A", "an", "An"])

def extractNE(tok, pnouns):
    names = LinkedList.LinkedList()
    #bag of words model
    tent = []
    prevword = "" #usually names are not preceded by an article - filters out some other named entities and some other cases
    for i in range(len(tok)):
        if STok.isuc(tok[i][0]) and (tok[i].lower() in pnouns) and (prevword not in articles):
            tent.append(tok[i])
        else:
            if len(tent) > 0 and type(tent): #will add if the named entity 
                matchNE(names, tent) #matches to most recent matching occurrence
                #sentencestarters.add(tent[0])
            tent = []
            prevword = tok[i]
    return names

def type(ent):
    for part in ent:
        if part in notperson:
            return False
    return True

def matchNE(names, ent):
    curnode = names.head
    match = False
    tname = NEName.Name(ent)
    if (tname): #is a name
        while (not match) and (curnode): #matching with older names in order of recency
            match = curnode.data.match(tname)
            if match: #refreshes node it is matched with
                curnode.data.update(tname) #updating
                tname = None #save space
                names.refresh(curnode)
            curnode = curnode.nextNode
        if not match: #adds node
            names.append(LinkedList.Node(tname))

def findPN(tok): #list of proper nouns
    #proper nouns will have positive indices, normal words negative
    pnoun = defaultdict(lambda: 0)
    for token in tok:
        ltoken = token.lower()
        if token == ltoken:
            pnoun[ltoken] -= 3
        else:
            pnoun[ltoken] += 1
    #list of words that are proper nouns
    pnouns = set([name for name in pnoun if pnoun[name] > 0])
    pnouns.remove("i")
    return pnouns

filetoread = "comt.txt"
text = open(filetoread, "r").read()
#tokens
tok = []
for sent in STok.stok(text): 
    tok.extend(word_tokenize(sent))
#proper nouns
names = extractNE(tok, findPN(tok))

name = names.head
NEs = {}
while name:
    NEs[name.data] = name.data.count
    name = name.nextNode
sNEs = sorted(NEs.iteritems(),key=lambda (k,v): v,reverse=True)
cutoff = math.sqrt(len(tok))
minorx = True
for i in range(len(sNEs)):
    if sNEs[i][1] < sNEs[0][1]*(i+1)/cutoff:
        break
    print sNEs[i][0].printout()[0] + " (" + str(sNEs[i][1]) + "), "