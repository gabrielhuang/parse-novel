'''
Created on May 4, 2015

@author: billyanhuang
'''
eos = set(["?", "!", ":", "\n", "--"]) #end of sentence symbols, not including period
titles = set(["Mr.", "Mrs.", "Ms.", "Miss", "Mister", "Dr.", "Doctor", "Sir", "Madam"]) #titles
suffixes = set(["Jr.", "Sr."]) #suffixes

def isc(char): #character
    return (ord(char) > 96 and ord(char) < 123) or (ord(char) > 64 and ord(char) < 91) or (ord(char) > 47 and ord(char) < 58)

def islc(char): #lowercase
    return (ord(char) > 96 and ord(char) < 123)

def isuc(char): #uppercase
    return (ord(char) > 64 and ord(char) < 91)

def issn(char): #space or newline or tab
    return (ord(char) == 32 or (ord(char) > 9 and ord(char) < 15))

#tokenizes sentences - does not include the period at the end of the sentence
def stok(text):
    text = text.replace('"', "") #removes quotation marks - not necessary for our purposes
    text = text.replace(" '", "") #removes quotation marks - not necessary for our purposes
    text = text.replace("' ", "") #removes quotation marks - not necessary for our purposes
    test = text.replace("--", " -- ")
    stok = [] #array of sentences
    sent = "" #current sentence
    
    for i in range(len(text)):
        #pesky -- usage in text...
        try:
            if text[i:i+2] in eos:
                if len(sent) > 0:
                    sent += " " + text[i:i+2] + " "
                    stok.append(sent)
                    sent = ""
                continue#i += 1
        except:
            pass
        #
        if text[i] in eos:
            if len(sent) > 0:
                sent += " " + text[i] + " "
                stok.append(sent)
                sent = ""
        elif text[i] == ".":
            end = True
            #end of sentence always followed by a space or something of the like
            try:
                end = issn(text[i+1])
            except:
                pass
            if end:
                #end of sentence is not followed by a lowercase character
                try:
                    ischar = False
                    j = 0
                    while not ischar:
                        j += 1
                        ischar = isc(text[i+j])
                    end = not islc(text[i+j])
                except:
                    pass
                if end:
                    #periods in names/titles/acronyms/initials
                    try:
                        if isuc(text[i-1]) or isuc(text[i-2]):
                            end = False
                    except:
                        pass
                    if end:
                        try:
                            if text[i-3:i] == "Mrs":
                                end = False
                        except:
                            pass
            if end:
                sent += " " + text[i] + " " #includes a space before
                stok.append(sent)
                sent = ""
            else:
                sent += text[i] #adds letter
        else:
            sent += text[i] #adds letter
        #eliminate spaces/new lines/tabs/etc. from beginning of sentence
        if len(sent) == 1 and issn(sent):
            sent = ""
    #returns
    return stok