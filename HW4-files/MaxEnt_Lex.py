import sys
import random
import math
from collections import defaultdict

# extract constraint names, candidates, violations, and frequency from input file
def load_data (d):
	lines = d.readlines()
	# this will store the tableaux, with words as keys
	tabs = defaultdict(lambda: defaultdict(lambda:[]))
	# this will store constraint/candidate names
	cnames = lines.pop(0).split()[3:]
	# this will store the index of each constraint/candidate
	cnum = defaultdict(lambda:0)
	for i in range(len(cnames)): cnum[cnames[i]] = i
	# this will store the class of each word
	wcat = defaultdict(lambda:'')
	# this will store frequencies of the words
	presf = defaultdict(lambda:0.0)
	pastf = defaultdict(lambda:0.0)
	lemmaf= defaultdict(lambda:0.0)
	for line in lines:
		fields = line.split()
		# get the word
		word = fields.pop(0)
		# get its frequency
		presf[word] = float(fields.pop(0))
		pastf[word] = float(fields.pop(0))
		lemmaf[word] = float(fields.pop(0))
		# find and store the word's category
		cat = cnames[fields.index('1')]
		wcat[word] = cat
		# create the tableau for this word
		# all candidates violate all constraints except
		# for the constraint corresponding to their class
		for cand in cnames:
			tabs[word][cand] = [1]*len(cnames)
			tabs[word][cand][cnum[cand]] = 0
	return (tabs,cnames,cnum,wcat,presf,pastf,lemmaf)

# using names, tableau, probs, and category of this example, 
# calculate expected (e) and observed (o) violations
def calcEO(n, tab, p, c):
	e = [0.0]* len(n) # [0.0] times however many names
	o = [0.0]* len(n) # [0.0] times however many names

	# PART 1: fill in the code to calculate e and o. 
	# Should be about 4 lines

	# frequency is 1 for the correct candidate and 0 for all the others
	candidates = list(tab.keys())

	# expected violations: sum over candidates (prob × vios)
	for i in range(len(n)):  # looping over each constraint (n = names)
		for j in range(len(candidates)): # looping over each candidate
			e[i] += p[j] * tab[candidates[j]][i] 

	# observed violations: take from the correct candidate (class c)
	for i in range(len(n)):
		o[i] = tab[c][i]

	return (e, o)

# using vios and weights, 
# calculate probabilities of all candidates
def calcP(w, s, snum, tab, scaled):
	# calculate probabilities assigned to candidates by current grammar
	p = []
	# also keep track of overall sum 'Z'
	z = 0.0
	for cand in tab:
		# keep track of harmony for each cand
		h = 0.0
		# go through each constraint
		for n in range(len(w)):
			# figure out if this constraint is the cloned one
			if n == snum and scaled:
				ind = 1.0
			else:
				ind = 0.0
			# add in the weight and scale for this violation
			h += tab[cand][n]*(w[n]+ind*s)
		p.append(math.exp(-h))
		z += math.exp(-h)
	p = [p[i]/z for i in range(len(tab))]
	return p

# print out frequencies or probabilities of candidates
def pretty_print(n, p):
	for i in range(len(n)):
		print("%15s - %.2f" % (n[i], p[i]))

def print_tab(s, tab):
	print("TABLEAU:", s)
	header = [""] + names + ["SCALE"]
	for h in header:
		print("%10s" % h, end = "")
	print("")
	grammar = weights + [scale[s]]
	print("%10s" % "", end = "")
	for w in grammar:
		print("%10.2f" % w, end = "")
	print("")
	for c in tab:
		print("%10s" % c, end = "")
		for v in tab[c]:
			print("%10s" % v, end = "")
		print("%10s" % tab[c][scalenum[s]])

# print out weights for all constraints
def print_w(w, n):
	for i in range(len(n)):
		print("%15s - %.2f" % (n[i], w[i]))

# BEGIN MAIN CODE

if len(sys.argv) == 4:
	# see function for info about what these variables are
	# takes training file, the number of iterations, and the learning rate
	# ex: Python MaxEnt_Lex.py TrainingData.txt 500000 .01
	(tableaux,names,cnum,wcat,presfreqs,pastfreqs,lemmafreqs)= load_data(open(sys.argv[1]))
	# names: list of constraints ['REG', 'NULL', 'X->{', 'X->$t', '5->u', 'g5->wEnt']
	# cnum: dictionary with each class and number {'REG': 0, 'NULL': 1, 'X->{': 2, 'X->$t': 3, '5->u': 4, 'g5->wEnt': 5}
	# wcat: dictionary of each word with its class
	iterations = int(sys.argv[2])
	rate = float(sys.argv[3])
	# scale_rate = rate * 2 # extra credit:  making the learning rate for scale updates bigger than the learning rate for weight updates
else:
	print("Incorrect number of command line arguments")
	print("USAGE:: MaxEnt_Lex.py data_file iterations learning_rate")
	sys.exit()

# weights on the general constrafints
weights = [1.0 for i in range(len(names))]
# weights[1] = 6 # extra credit: setting the initial weight of the NULL constraint higher than the others
# print(weights) -> [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
# start with initial weights = 1.0 for all constraints

# a scale for each word
# scale stores the strength of the scale
scale = defaultdict(lambda: 0.0)
# scalenum stores the index of constraint that the scale copies
scalenum = defaultdict(lambda: 0)
for word in tableaux:
	scalenum[word] = cnum[wcat[word]] # word: number from cnum (constraint/category that scale copies)

# L2 prior on the weights
sigma2 = [100 for i in range(len(names))]
mu = [0.0 for i in range(len(names))]
# L2 prior on the scales
scale_mu = 0.0
scale_sigma2 = 100

# this list stores examples words to track in output
examples = ['juz->juzd','krImp->krImpt', 'sEt->sEt', 'Tr5->Tru', 'drINk->dr{Nk','TINk->T$t','b2->b$t','g5->wEnt', 'gr5->gru', 'n5->nju']


# what frequency distribution to use for training
unifreqs = defaultdict(lambda: 1.0)
for w in presfreqs: unifreqs[w] = 1.0
freqs = pastfreqs


for iter in range(iterations):
	# sample a training item from the distribution
	sample = random.choices(list(freqs.keys()),freqs.values(),k=1)[0]
	# print_tab(sample,tableaux[sample])

	# calculate the probabilities of each candidate given the current weights and scale
	probs = calcP(weights, scale[sample], scalenum[sample], tableaux[sample], True)
 
 	# calculate the expected and observed violations for each constraint
	(exp, obs) = calcEO(names, tableaux[sample], probs, wcat[sample])
	# same for the scale. it just copies values from its parent constraint
	scaleE = exp[scalenum[sample]]
	scaleO = obs[scalenum[sample]]
	
	# update the weights for each constraint based on exp, obs
	for i in range(len(names)):
		weights[i] -= rate * (obs[i]-exp[i] + (weights[i]-mu[i])/sigma2[i])
		weights[i] = max(weights[i],0.0) #if constraint weight is negative, will invert the intended effect of the weight

	# update the scale for the sampled word: 
	# PART 2 code goes here: should be 2 lines
	scale[sample] -= rate * (scaleO-scaleE + (scale[sample]-scale_mu)/scale_sigma2)
	# scale[sample] -= scale_rate * (scaleO-scaleE + (scale[sample]-scale_mu)/scale_sigma2) # extra credit
	scale[sample] = max(scale[sample],0.0) #if constraint weight is negative, will invert the intended effect of the weight

	if iter % 100 == 0:
		print("STARTING ITERATION: " + str(iter))
		print("New Weights")
		pretty_print(names,weights)
		nonce_probs = calcP(weights, scale[sample], scalenum[sample], tableaux[sample], False)
		print("New nonce predictions")
		pretty_print(names,nonce_probs)
		print("Predictions for Example Items:")

		logprob = 0.0
		for w in freqs:
			probs = calcP(weights, scale[w], scalenum[w], tableaux[w], True)
			logprob += freqs[w]*math.log(probs[cnum[wcat[w]]])
			if w in examples:
				print("Item and Scale:",w, scale[w])
				print("New Scaled Probs")
				probs = calcP(weights, scale[w], scalenum[w], tableaux[w], True)
				pretty_print(names,probs)
		print("logprobability of the data: ", logprob)