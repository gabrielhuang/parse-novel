# -*- coding: utf-8 -*-
'''
@brief Transform text into sentences.
@date May 2015
@author Gabriel Huang

This module (STok2) is designed to be interchangeable with module STok
Built upon billyanhuang's contribution
'''
import re

######## Stuff for compatibility with STok ########
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
################################

nonperiod_eos = re.compile(r'[\?\!:]') # non-period end of sentences
drop_symbols = re.compile(r'("|--|[\n\t\ \'])+')
specials = set(['Mr', 'Mrs', 'Ms', 'Jr', 'Sr'])

def stok(txt):
    preprocessed = drop_symbols.sub(' ', txt) # replace
    undersegmented = nonperiod_eos.split(preprocessed)
    sentences = []
    for us in undersegmented:
        oversegmented = us.split('.')
        acc = []
        for os in oversegmented:
            words = os.split()
            if words and words[-1] in specials:
                acc.append(os)
            else: # doesnt end with special, join with previous specials
                acc.append(os)                
                sentences.append('.'.join(acc))
                acc = []
        if acc:
            sentences.append('.'.join(acc))
    return sentences

# Test
if __name__=='__main__':
    txt = '''For a moment the last sunshine fell with romantic affection upon her glowing face; her voice compelled me forward breathlessly as I listened--then the glow faded, each light deserting her with lingering regret like children leaving a pleasant street at dusk.

The butler came back and murmured something close to Tom's ear whereupon Tom frowned, pushed back his chair and without a word went inside. As if his absence quickened something within her Daisy leaned forward again, her voice glowing and singing.

"I love to see you at my table, Nick. You remind me of a--of a rose, an absolute rose. Doesn't he?" She turned to Miss Baker for confirmation. "An absolute rose?"

This was untrue. I am not even faintly like a rose. She was only extemporizing but a stirring warmth flowed from her as if her heart was trying to come out to you concealed in one of those breathless, thrilling words. Then suddenly she threw her napkin on the table and excused herself and went into the house.

Miss Baker and I exchanged a short glance consciously devoid of meaning. I was about to speak when she sat up alertly and said "Sh!" in a warning voice. A subdued impassioned murmur was audible in the room beyond and Miss Baker leaned forward, unashamed, trying to hear. The murmur trembled on the verge of coherence, sank down, mounted excitedly, and then ceased altogether.

"This Mr. Gatsby you spoke of is my neighbor----" I said.

"Don't talk. I want to hear what happens."

"Is something happening?" I inquired innocently.

"You mean to say you don't know?" said Miss Baker, honestly surprised. "I thought everybody knew."

"I don't."

"Why----" she said hesitantly, "Tom's got some woman in New York."

"Got some woman?" I repeated blankly.
'''
    sentences = stok(txt)
    for s in sentences:
        print s
 
    import STok
    reference = STok.stok(txt)
    for s in reference:
        print s