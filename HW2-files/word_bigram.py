import re
import sys
import random
from collections import defaultdict

# keeps generating words until # is randomly generated, then returns the whole sentence
def generate_sentence():
    sentence = "#" #initial token in 'sentence'
    current = '' #keeps track of current token
    while current != '#': #while not at end of word
        if current == '': current = '#' #need pound symbol for generate_word
        current = generate_word(current) #generates random 'word' (token) to add to 'sentence' (word)
        sentence += " " + current #adds token to 'sentence'
    return sentence

#given a word, randomly generates and returns the next word using the bigram model
def generate_word(word):
    # generate a random float between 0 and 1
    # we will use this float to probabilistically select a 'bin'
    # corresponding to a word in our bigram model
    rand = random.uniform(0,1)
    # go through each possible second word
    for following in bigram[word]:
        # subtract this word's probability from rand 
        rand -= bigram[word][following]
        # as soon as we 'cross over' zero we have found the word for that bin
        if rand < 0.0: return following
    return following	

# open file for training the bigram model
language = open(sys.argv[1]) 

# defaultdict takes a lambda function as an argument and uses it to set the default value for every key
# this makes it easy to build up the dictionaries without checking for each key's existence
counts = defaultdict(lambda:0) #stores each character that occurs in txt file and how many times it occurs
bicounts = defaultdict(lambda:defaultdict(lambda:0)) #stores each character that occurs in txt file and nested dict of characters that occur after it and how many times they do so

# this loops through all the data and stores counts
for line in language:
    # we have to have a way to begin and end each line
    line = "# " + line.strip() + " #" #strip removes extra spaces
    words = re.split(r'[,.?"!\s:;]+|--', line) #word as a list containing each character, including # symbols

    # we go through each position and keep track of word and word pair counts
    for i in range(len(words)-1):
        counts[words[i]] = counts[words[i]] + 1
        bicounts[words[i]][words[i+1]] = bicounts[words[i]][words[i+1]] + 1

language.close()

bigram = defaultdict(lambda:{})

# this loops through all word pairs and computes relative frequency estimates
for word1 in counts:
    for word2 in bicounts[word1]:
        bigram[word1][word2] = float(bicounts[word1][word2])/float(counts[word1])
        print("P(" + word2 + " | " + word1 + ")\tis\t" + str(bigram[word1][word2]))
        #probability of seeing first thing given that you've just seen second thing



# print 20 random 'sentences' using the bigram
for i in range(20):
    print(generate_sentence())