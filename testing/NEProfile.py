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

#weights for BoW
a = 20
b = 15
weights = [a]
dist = 0
while weights[dist] >= 1:
    dist += 1
    weights.append(int(a*math.pow(math.e, -math.pow(((float(dist))/(float(b))), 2))))

titles = set(["Mr.", "Mrs.", "Ms.", "Miss", "Mister", "Dr.", "Doctor", "Monsieur", "Madame", 
              "Monseigneur", "Sir", "Lady", "M.", "Mme.", "Mademoiselle"]) #titles
suffixes = set(["Jr.", "Sr."]) #suffixes

notperson = set(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
                 "East", "West", "North", "South",
                 "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", 
                 "Street", "Road", "Avenue",
                 "York", "Chicago", "Los", "San", "Oxford", "Paris",
                 "America", "American", "France", "French", "English", "England",
                 "Project", "Chapter",
                 "Island", "Coast", "Bay", "Sound",
                 "Oh", "Yeah", "Aw", "Aww", "Ohh", "O", "Mr", "Mrs", "Ah", "Ahh",
                 "Original",
                 "Yes", "No", "God", "Please"]) #common sentence starters
articles = set(["the", "The", "a", "A", "an", "An"])

def extractNE(tok, pnouns, dic):
    names = LinkedList.LinkedList()
    nameprofs = defaultdict(lambda: defaultdict(lambda: 0))
    #bag of words model
    tent = []
    prevword = "" #usually names are not preceded by an article - filters out some other named entities and some other cases
    for i in range(len(tok)):
        if STok.isuc(tok[i][0]) and (tok[i].lower() in pnouns) and (prevword not in articles):
            tent.append(tok[i])
        else:
            if len(tent) > 0 and type(tent): #will add if the named entity 
                match = matchNE(names, tent) #matches to most recent matching occurrence
                
                for j in range(0, len(weights)):
                    try:
                        word = tok[i+j].lower()
                        if (word not in pnouns) and len(word) > 3 and ("," not in word) and (word in dic):
                            nameprofs[match][word] += weights[j]
                    except:
                        break
                for j in range(0, len(weights)):
                    try:
                        word = tok[i-len(tent)-j-1].lower()
                        if (word not in pnouns) and len(word) > 3 and ("," not in word) and (word in dic):
                            nameprofs[match][word] += weights[j]
                    except:
                        break
                
            tent = []
            prevword = tok[i]
    return [names, nameprofs]

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
                return curnode.data
            curnode = curnode.nextNode
        if not match: #adds node
            names.append(LinkedList.Node(tname))
            return names.head.data

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

def tfidf(namebow, textbow, dic): #tfidf on word counts
    print 1000*sizeOf(namebow)/sizeOf(textbow)
    for word in namebow:
        try:
            dif = math.log10(dic[word])
        except:
            dif = 2
        namebow[word] = (1000*(namebow[word]-dif)/(a + textbow[word]))*(1 - math.pow(math.log10(dif+1), namebow[word]))
    sbow = sorted(namebow.iteritems(),key=lambda (k,v): v,reverse=True)
    return sbow[:10]

def sizeOf(dic): #number of occurrences
    size = 0
    for word in dic:
        size += dic[word]
    return size

def generateDic(tok): #text word counts
    dic = defaultdict(lambda: 0)
    for word in tok:
        dic[word] += 1
    return dic

filetoread = "../data/gatsby.txt"
text = open(filetoread, "r").read()
#tokens
tok = []
for sent in STok.stok(text): 
    tok.extend(word_tokenize(sent))
#proper nouns

f = open("../data/coca", "r")
global dic
dic = {}
for line in f:
    stri = line.split()
    dic[stri[0]] = int(stri[1])
    
names = extractNE(tok, findPN(tok), dic)

name = names[0].head
nameprofs = names[1]

textdic = generateDic(tok)

NEs = {}
while name:
    NEs[name.data] = name.data.count
    name = name.nextNode
sNEs = sorted(NEs.iteritems(),key=lambda (k,v): v,reverse=True)
cutoff = math.sqrt(len(tok))
minorx = True
for i in range(len(sNEs)):
    if sNEs[i][1] < sNEs[0][1]*(i+1)/cutoff:
        print sNEs[0][1]*(i+1)/cutoff
        break
    print sNEs[i][0].printout()[0] + " (" + str(sNEs[i][1]) + "), "
    print tfidf(names[1][sNEs[i][0]], textdic, dic)