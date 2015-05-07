'''
Created on May 5, 2015

@author: billyanhuang
'''
titles = set(["Mr.", "Mrs.", "Ms.", "Miss", "Mister", "Dr.", "Doctor", "Monsieur", "Madame"]) #titles
ctitles = []
ctitles.append(set(["Mr.", "Mister", "Monsieur", "Marquis"]))
ctitles.append(set(["Mrs.", "Ms.", "Miss", "Madame"]))
ctitles.append(set(["Dr.", "Doctor"]))
suffixes = set(["Jr.", "Sr."]) #suffixes

class Name:
    t = "" #title
    s = "" #suffix
    f = "" #first name
    m = "" #middle name
    l = "" #last name
    fl = "" #not known - single word references to characters can be either first or last name
    count = 0 #number of times it appears
    
    def __init__(self, ent):
        #count and occurrence initialization
        self.count = 1
        
        l = len(ent)
        #title and suffix
        t = 0
        if ent[0] in titles:
            self.t = ent[0]
            t = 1
        else:
            self.t = ""
        s = 0
        if ent[l-1] in suffixes:
            self.s = ent[l-1]
            s = 1
        else:
            self.s = ""
        #name components
        l = l-t-s
        if l == 3:
            self.f = ent[t]
            self.m = ent[t+1]
            self.l = ent[t+2]
            self.fl = ""
        elif l == 2:
            self.f = ent[t]
            self.m = ""
            self.l = ent[t+1]
            self.fl = ""
        elif l == 1:
            if t == 1:   
                self.f = ""
                self.m = ""
                self.l = ent[t]
                self.fl = ""
            else:
                self.f = ""
                self.m = ""
                self.l = ""
                self.fl = ent[t]
        else:
            self = None
        if (self == None) or ((self.f in titles) or (self.m in titles) or (self.l in titles) or (self.fl in titles) or 
            (self.f in suffixes) or (self.m in suffixes) or (self.l in suffixes) or (self.fl in suffixes)):
            self = None
    
    def update(self, other):
        if len(other.t) > len(self.t):
            self.t = other.t
        if len(other.f) > len(self.f):
            self.f = other.f
            self.fl = ""
        if len(other.m) > len(self.m):
            self.m = other.m
        if len(other.l) > len(self.l):
            self.l = other.l
            self.fl = ""
        if len(other.s) > len(self.s):
            self.s = other.s
        #update count and occurrence
        self.count += 1
            
    def match(self, other):
        poss = True #no conflicting names
        match = False #something matches
        #titles/suffixes
        if (len(self.t)*len(other.t) > 0) and poss:
            if not sametitle(other.t, self.t):
                poss = False
        if (len(self.s)*len(other.s) > 0) and poss:
            if not other.s == self.s:
                poss = False
        #names
        if (len(self.f)*len(other.f) > 0) and poss:
            if samename(other.f, self.f):
                match = True
            else:
                poss = False
        if (len(self.m)*len(other.m) > 0) and poss:
            if not samemiddle(other.m, self.m):
                poss = False
        if (len(self.l)*len(other.l) > 0) and poss:
            if samename(other.l, self.l):
                match = True
            else:
                poss = False
        #case of ambiguous first/last name
        if poss and len(other.fl) > 0:
            if (samename(other.fl, self.f) or samename(other.fl, self.l) or samename(other.fl, self.fl)):
                match = True
            else:
                poss = False
        if poss and len(self.fl) > 0:
            if (samename(self.fl, other.f) or samename(self.fl, other.l) or samename(self.fl, other.fl)):
                match = True
            else:
                poss = False
        #returning
        return (poss and match)
    
    def printout(self):
        return (self.get_data(), self.get_count())
    
    def get_data(self):
        info = ""
        if len(self.t) > 0:
            info += self.t + " "
        if len(self.f) > 0:
            info += self.f + " "
        if len(self.m) > 0:
            info += self.m + " "
        if len(self.l) > 0:
            info += self.l + " "
        if len(self.fl) > 0:
            info += self.fl + " "
        if len(self.s) > 0:
            info += self.s + " "
        return info[:-1]
        
    def get_count(self):
        return self.count
    
    def __str__(self):
        return str(self.printout()[0])

def samename(n1, n2): #first/last names
    try:
        same = False
        if n1 == n2:
            same = True
        return same
    except:
        return False

def samemiddle(m1, m2): #middle name
    try:
        same = False
        if m1 == m2:
            same = True
        if m1[0] == m2[0] and (m1[1] == "." or m2[1] == "."):
            same = True
        return same
    except:
        return False
    
def sametitle(t1, t2):
    same = False
    for titset in ctitles:
        if t1 in titset and t2 in titset:
            same = True
            break
    return same
