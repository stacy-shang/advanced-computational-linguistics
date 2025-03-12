import re
import sys
import random
import math
from collections import defaultdict

# keeps generating words until # is randomly generated, then returns the whole sentence
def bigram_generate_sentence():
    sentence = "#" # initial token in 'sentence'
    current = '' # keeps track of current token
    while current != '#': # while not at end of word
        if current == '': current = '#' # need # symbol for generate_word
        current = bigram_generate_word(current) #generates random 'word' (token) to add to 'sentence' (word)
        sentence += " " + current # adds token to 'sentence'
    return sentence

# generates a sentence using the trigram model
def trigram_generate_sentence():
    sentence = ["#", "#"]  # initialize with two # symbols
    current_context = ("#", "#")  # tuple to track last two words (trigram context)
    while True:  # infinite loop, break manually when # symbol is found
        following = trigram_generate_word(current_context)  # get next word from trigram model
        sentence.append(following)  # append new word to sentence
        current_context = (sentence[-2], sentence[-1])  # update context to last two words 
        if following == "#":  
            break  # break if end token is reached
    return " ".join(sentence)  # return the sentence

# given a word, randomly generates and returns the next word using the bigram model
def bigram_generate_word(word):
    # generate a random float between 0 and 1
    # we will use this float to probabilistically select a 'bin'
    # corresponding to a word in our bigram model
    rand = random.uniform(0,1)
    # go through each possible second word
    for following in bigram_probabilities[word]:
        # subtract this word's probability from rand 
        rand -= bigram_probabilities[word][following]
        # as soon as we 'cross over' zero we have found the word for that bin
        if rand < 0.0: return following
    return following	

# generates the next word using the trigram model probabilities
def trigram_generate_word(context):
    rand = random.uniform(0, 1)
    for following in trigram_probabilities[context]:
        rand -= trigram_probabilities[context][following]
        if rand < 0.0:
            return following

# open file for training the bigram model
language = open(sys.argv[1])
n = int(sys.argv[2])

# defaultdict takes a lambda function as an argument and uses it to set the default value for every key
# this makes it easy to build up the dictionaries without checking for each key's existence
counts = defaultdict(lambda:0) # stores each character that occurs in txt file and how many times it occurs
bicounts = defaultdict(lambda:defaultdict(lambda:0)) # stores each character that occurs in txt file and nested dict of characters that occur after it and how many times they do so
tricounts = defaultdict(lambda: defaultdict(lambda: 0))  # stores trigram counts in a nested list that contains tuples with (word1, word2) as keys, and dictionaries containing possible following words and their probabilities

### SMOOTHING
if len(sys.argv) == 4:
    
    # set up vocabulary of unique words
    vocab = set()  # store unique words

    # read the dataset once to collect all words for a consistent vocabulary
    for line in language:
        parts = line.strip().split(maxsplit=1)
        transcription = parts[1]
        transcription = "# # " + transcription.strip() + " #"  # padding
        words = re.split(r'[,.?"!\s:;]+|--', transcription)

        for word in words:
            vocab.add(word)  # add every word to the vocabulary

    vocab_size = len(vocab)  # store vocabulary size for smoothing
    language.seek(0) # go back to beginning of language for later

    ### BIGRAMS SMOOTHING
    if n == 2:
        for line in language:
            parts = line.strip().split(maxsplit = 1)  # split line into word and transcription
            transcription = parts[1]  # extract only the phonetic transcription
            transcription = "# " + transcription + " #" # padding
            words = re.split(r'[,.?"!\s:;]+|--', transcription)  # split transcription into tokens

            # go through each position and keep track of word and word pair counts
            for i in range(len(words)-1):
                counts[words[i]] = counts[words[i]] + 1
                bicounts[words[i]][words[i+1]] = bicounts[words[i]][words[i+1]] + 1

        language.close()

        bigram_probabilities = defaultdict(lambda:defaultdict(lambda:0))

        # this loops through all word pairs and computes relative frequency estimates
        
        # smoothing over all possible bigrams
        for word1 in vocab:
            for word2 in vocab:
                bigram_probabilities[word1][word2] = (bicounts[word1][word2] + 1) / (counts[word1] + vocab_size)

        test_file = open(sys.argv[3])
        test_words = [line.strip() for line in test_file.readlines()]
        test_file.close()

        nonce_words = [] # create list to contain nonce words with # symbols appended
        for word in test_words:
            word = "# " + word + " #"
            nonce_words.append(word)

        N = 0 # count number of bigram probabilities multiplied together
        log_sum = 0 # sum of logs for perplexity formula
        for nonce_word in nonce_words:
            word = nonce_word.split() #### added this - Eva
            word_log_prob = 0 # sum of log probabilities to exponentiate later
            for i in range(len(word) - 1):
                word1, word2 = word[i], word[i + 1]
                log_prob = math.log(bigram_probabilities[word1][word2], 2) # take log of bigram probability
                word_log_prob += log_prob
                log_sum += log_prob
                N += 1
            word_prob = 2**word_log_prob # exponentiate because the log sum for words multiplied together is negative
            print(f'{nonce_word}    {word_prob}')
            
        perplexity = 2**(log_sum*((-1)/N)) # calculate perplexity
        print(f'Perplexity: {perplexity}')
    
    ### TRIGRAMS SMOOTHING
    if n == 3:
        for line in language:
            parts = line.strip().split(maxsplit = 1)  # split line into word and transcription
            transcription = parts[1]  # extract only the phonetic transcription
            transcription = "# # " + transcription.strip() + " #" # padding
            words = re.split(r'[,.?"!\s:;]+|--', transcription)

            for i in range(len(words) - 2):
                context = (words[i], words[i + 1])  # trigram context
                following = words[i + 2]  # third word (prediction)
                tricounts[context][following] += 1  # store count

        language.close()

        # compute trigram probabilities
        trigram_probabilities = defaultdict(lambda:defaultdict(lambda:0))

        # smoothing over all possible trigrams
        for word1 in vocab:
            for word2 in vocab:
                context = (word1, word2) # getting every possible pair for context
                denominator = sum(tricounts.get(context, {}).values()) + vocab_size
                # sum up all of times words have appeared after context, add vocab size for smoothing
                # if context does not appear in tricounts, get empty dictionary (sum of that is zero)
                for word3 in vocab:
                    trigram_probabilities[context][word3] = (tricounts.get(context, {}).get(word3, 0) + 1) / denominator
                    # get number of occurences of word3 following context, add one for smoothing
                    # if context not in tricounts, get empty dictionary, and if word3 never follows context, get zero
                    # divide by denominator calculated earlier
        
        test_file = open(sys.argv[3])
        test_words = [line.strip() for line in test_file.readlines()]
        test_file.close()

        nonce_words = [] # create list to contain nonce words with # symbols appended
        for word in test_words:
            word = "# # " + word + " #"
            nonce_words.append(word)

        N = 0 # count number of bigram probabilities multiplied together
        log_sum = 0 # sum of logs for perplexity formula
        for nonce_word in nonce_words:
            word = nonce_word.split() #### added this - Eva
            word_log_prob = 0 # sum of log probabilities to exponentiate later
            for i in range(len(word) - 2):
                word1, word2, word3 = word[i], word[i + 1], word[i + 2]
                context = (word1, word2)
                log_prob = math.log(trigram_probabilities[context][word3], 2) # take log of trigram probability
                word_log_prob += log_prob
                log_sum += log_prob
                N += 1
            word_prob = 2**word_log_prob # exponentiate because the log sum for words multiplied together is negative
            print(f'{nonce_word}    {word_prob}')
            
        perplexity = 2**(log_sum*((-1)/N))
        print(f'Perplexity: {perplexity}')


### NOT SMOOTHING (generating words)
else:
    ### BIGRAMS GENERATING SENTENCES
    if n == 2:
        # read the file and extract only phonetic transcriptions (excluding first column)
        for line in language:
            parts = line.strip().split(maxsplit = 1)  # split line into word and transcription
            transcription = parts[1]  # extract only the phonetic transcription

            transcription = "# " + transcription + " #"
            words = re.split(r'[,.?"!\s:;]+|--', transcription)  # split transcription into tokens

            # go through each position and keep track of word and word pair counts
            for i in range(len(words)-1):
                counts[words[i]] = counts[words[i]] + 1
                bicounts[words[i]][words[i+1]] = bicounts[words[i]][words[i+1]] + 1

        language.close()

        bigram_probabilities = defaultdict(lambda:defaultdict(lambda:0))

        # this loops through all word pairs and computes relative frequency estimates
        for word1 in counts:
            for word2 in bicounts[word1]:
                bigram_probabilities[word1][word2] = bicounts[word1][word2] / counts[word1]

        for i in range(25):
            print(bigram_generate_sentence())

    ### TRIGRAMS GENERATING SENTENCES
    if n == 3:
        for line in language:
            parts = line.strip().split(maxsplit = 1)  # split line into word and transcription
            transcription = parts[1]  # extract only the phonetic transcription
            transcription = "# # " + transcription.strip() + " #" # padding
            words = re.split(r'[,.?"!\s:;]+|--', transcription)  # tokenize words

            for i in range(len(words) - 2):
                context = (words[i], words[i + 1])  # trigram context
                following = words[i + 2]  # third word (prediction)
                tricounts[context][following] += 1  # store count

        language.close()

        # compute trigram probabilities
        trigram_probabilities = defaultdict(lambda: {})

        for context in tricounts:
            total_count = sum(tricounts[context].values()) # sum of all occurrences of context in tricounts
            for following in tricounts[context]:
                trigram_probabilities[context][following] = tricounts[context][following] / total_count

        # generate 25 random sentences using the trigram model
        for i in range(25):
            print(trigram_generate_sentence())