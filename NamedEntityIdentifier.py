'''
Created on May 4, 2015

@author: billyanhuang
'''
import STok #works better than the nltk one
import NEName #class for character names and comparisons
import LinkedList #recency-based coreference
from nltk.tokenize import word_tokenize
from nltk import defaultdict
import nltk
import math

#name stuffs
titles = set(["Mr.", "Mrs.", "Ms.", "Miss", "Mister", "Dr.", "Doctor", "Monsieur", "Madame"]) #titles
suffixes = set(["Jr.", "Sr."]) #suffixes
notperson = set(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
                 "East", "West", "North", "South",
                 "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
                 "Street", "Road", "Avenue",
                 "York", "Chicago", "Los", "San", "Oxford",
                 "Island", "Coast", "Bay", "Sound",
                 "The", "A", "An", "That", "There", "This", "Thus", "How", "Where", "When", "Why", "Who",
                 "Father", "Mother", "His", "Her", "He", "She", "It", "Its", "You", "I",
                 "Not", "Never", "And", "Or", "But", "Then", "After", "Before",
                 "Some", "Many", "Few", "In", "To", "If", "Do", "For", "So",
                 "God", "Yeah", "Well", "Aw",
                 "My", "Hers", "Our", "We", "Oh", "They",
                 "Yes", "No", "Now", "What",
                 "Is", "As"])   #can add a lot more - stopwords, dates, proper nouns, etc.
                                #will probably thoroughly make a set later

def type(ent):
    for part in ent:
        if part in notperson:
            return False
    return True

def tokenize(text):
    #tokenizes into words
    tok = []
    for sent in STok.stok(text): 
        tok.extend(word_tokenize(sent))
    return tok
        
def extractNE(tok):
    names = LinkedList.LinkedList()
    sentencestarters = titles.copy()
    #bag of words model
    namedic = defaultdict(lambda: defaultdict(lambda: 0)) #each name has an associated sparse vector, shallow copy since vectors consist of integers
    #extracts named entities
    tent = []
    sentencestarter = True
    for i in range(len(tok)):
        if sentencestarter: #first word of sentence - tricky source of error
            if tok[i] in sentencestarters:
                tent.append(tok[i])
            sentencestarter = False
        else:
            if STok.isuc(tok[i][0]) and (tok[i] != "I"): #appending terms to named entity
                tent.append(tok[i])
            else:
                if len(tent) > 0 and type(tent): #will add if the named entity 
                    matchNE(names, tent) #matches to most recent matching occurrence
                    #sentencestarters.add(tent[0])
                tent = []
            if tok[i] in STok.eos or tok[i] == ".":
                sentencestarter = True
    return [names, namedic, sentencestarters]
    
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

###################################################################################################

def modmatch(names, ent): #matches occurrence to a named entity
    curnode = names.head
    match = False
    tname = NEName.Name(ent)
    if (tname): #is a name
        while curnode: #matching with older names in order of recency
            match = curnode.data.match(tname)
            if match: #refreshes node it is matched with
                tname = None #save space
                names.refresh(curnode)
                return curnode.data
            curnode = curnode.nextNode
    return None

def detectNE(res, par): #detects occurrences, matches, and keeps track
    detected = []
    partok = tokenize(par) #tokenizing paragraph into wordstent = []
    tent = [] #temporary entity
    sentencestarter = True #beginning of sentence
    for i in range(len(partok)):
        if sentencestarter: #first word of sentence - tricky source of error
            if partok[i] in res[2]:
                tent.append(partok[i])
            sentencestarter = False
        else:
            if STok.isuc(partok[i][0]) and (partok[i] != "I"): #appending terms to named entity
                tent.append(partok[i])
            else:
                if len(tent) > 0 and type(tent): #will add if named entity 
                    detected.append([modmatch(res[0], tent), i-len(tent)]) #if matches, adds name and location
                tent = []
            if partok[i] in STok.eos or partok[i] == ".":
                sentencestarter = True
    return detected

###################################################################################################

filetoread = "text.txt"

text = open(filetoread, "r").read()
tok = tokenize(text)
NEs = {} #final named entities
res = extractNE(tok)

#printing out ranking by prevalence and correlated adjectives
name = res[0].head
while (name): #iterating over all named entities
    info = name.data.printout()
    NEs[name.data] = info[1]
    name = name.nextNode
sNEs = sorted(NEs.iteritems(),key=lambda (k,v): v,reverse=True) #sorted by count
for name in sNEs: #output
    if name[1] < 10:
        break
    print name[0].printout()[0] + " " + str(name[1])
    res[2].add(name[0].t)
    res[2].add(name[0].f)
    res[2].add(name[0].l)

###
partoread = "par.txt"
detected = detectNE(res, open(partoread, "r").read())
for entity in detected:
    try:
        print str(entity[1]) + ", " + entity[0].printout()[0] #name and word # in text
    except:
        pass
###
