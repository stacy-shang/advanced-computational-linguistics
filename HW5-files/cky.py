import sys
from collections import defaultdict

# given the grammar file name, create dictionary storing the grammar and return it
# each key of the dictionary is a RHS (right hand side), which is tuple of symbols, such as ("Det","N")
# for each key, the dictionary stores a list of "rules"
# each "rule" is itself a list of three things, the LHS, the logprob, and the RHS
# for example one "rule" would be ['NP', 3.70, ("Det","N")]
def readGrammarFile(fn):
    grammar_dict = {}
    for line in open(fn):
        if line.strip() == '': continue
        columns = line.split()
        logprob = float(columns[0])
        lhs = columns[1]
        rhs = tuple(columns[2:])
        if rhs not in grammar_dict:
            grammar_dict[rhs] = []
        rules = [lhs, logprob, rhs]
        grammar_dict[rhs].append(rules)
    # print(grammar_dict)
    return grammar_dict

# if you use the suggested format for the CKY chart
# you can use this function to print out the chart and doublecheck your work
def print_table(table,words):
    cols = len(table[0])
    rows = len(table)
    for c in range(1,cols):
        print(f'{words[c-1]:10}',end="")
    print()
    for r in range(rows):
        for c in range(1,cols):
            if table[r][c]:
                print (f'{",".join([table[r][c][i][0] for i in range(len(table[r][c]))]):10}', end = "")
            else:
                print(' '*10, end="")
        print()

# For every parse in the table, print it and its weight out
# If there is no parse, print 'No Parse!'
# Hint: you may want to write and call another, recursive function to print out the parse
def print_tree(table):
    n = len(table)
    if table[0][n] == []:
        print("No Parse!")
        print()
        return
    else:
        tree_count = 1
        for root in table[0][n]:
            if root[0] != 'ROOT':
                print("No Parse!")
                print()
                return
            print(f'Tree {tree_count} weight: {root[1]}')
            print(f'Tree {tree_count} parse:')
            print("( ROOT ( " + recursive(table, root[2]) + " ) ( " + recursive(table, root[3]) + " ) )")
            # print("[ ROOT [ " + recursive(table, root[2]) + " ] [ " + recursive(table, root[3]) + " ] ]") # brackets for putting into syntax tree generator
            print()
            tree_count += 1

def recursive(table, backpt):
    curr = table[backpt[1]][backpt[2]][backpt[3]]
    if len(curr) == 3:
        return(f'{curr[0]} {curr[2]}')
    elif len(curr) == 4:
        return curr[0] +" ( " + recursive(table, curr[2]) + " ) ( " + recursive(table, curr[3]) + " )"
        # return curr[0] +" [ " + recursive(table, curr[2]) + " ] [ " + recursive(table, curr[3]) + " ]" # brackets for putting into syntax tree generator


# given a grammar dictionary and a string of words, return the CKY chart
# in each cell of the chart, there is a list of 'states'
# each 'state' is a tuple with the nonterminal label, logprob of that state, references to the child states
# since this grammar is in Chomsky Normal Form...
# 'states' will have length 4 for nonterminals and length 3 for preterminals
def cky(gr, words):
    n = len(words)
    # n will be the number of columns to walk through
    # make a table with n+1 columns and n rows with None in each cell
    table = [[None]*(n+1) for i in range(n)]

    #Your code to fill in the CKY chart goes here
    for j in range(1, n+1): # diagonal
        word = words[j-1] # current word in loop
        rhs = (word,) # tuple to search keys in grammar dict
        if rhs in gr: # if rhs is in the grammar, set cell equal to empty list instead of None
            table[j - 1][j] = []
            for rule in gr[rhs]: # for each rule that rhs has, append tuple w/ nonterm label, logprob to list in cell
                nonterminal_label = rule[0]
                logprob = rule[1]
                state = (nonterminal_label, logprob, word)
                table[j - 1][j].append(state)
        for i in range(j-2, -1, -1): # for i <- from j-2 downto 0 
            for k in range(i+1, j): # for k <- i+1 to j-1 
                if table[i][k] is None or table[k][j] is None:
                    continue # skip if either side of split is None
                elif table[i][j] == None:  table[i][j] = [] ############## added this
                B_states = table[i][k] # list of states (tuples w/ nonterm label, logprob) that are in B cell
                C_states = table[k][j] # list of states (tuples w/ nonterm label, logprob) that are in C cell
                for b in range(len(B_states)): # loop thru every possible combo of B and C states to create rhs and check if in grammar
                    b_state = B_states[b]
                    for c in range(len(C_states)):
                        c_state = C_states[c]
                        b_label = b_state[0] # nonterm label of tuple
                        c_label = c_state[0] # nonterm label of tuple
                        rhs_BC = (b_label,c_label) # tuple format of rhs for checking grammar
                        if rhs_BC not in gr: # if rhs is not in grammar, continue
                            continue
                        for rule in gr[rhs_BC]: 
                            nonterminal_label = rule[0]
                            logprob = rule[1] + b_state[1] + c_state[1]
                            b_backpt = (b_label, i,k,b)
                            c_backpt = (c_label, k,j,c)
                            state = (nonterminal_label, logprob, b_backpt, c_backpt)
                            table[i][j].append(state) ########## changed this from table[i][j] = state
                
    # print_table(table,words)
    # print(table)
    return table

### MAIN ###

if len(sys.argv) != 3:
    print ("USAGE: cky.py GRAMMAR_FILE SENTENCE_FILE")
    exit(0)

file = sys.argv[1] # grammar file
sentences = sys.argv[2] # sentence file

# read in the grammar and store it as a dictionary called 'grammar'
grammar = readGrammarFile(file)

for line in open(sentences): # loop thru each sentence
    if line.strip() == '': break # remove leading/trailing whitespace from sentence, break if encounters empty string
    print ("PARSING::\t", line.strip()) # PARSING: whatever the sentence is
    words = line.split() # splits sentence on individual words
    # use the grammar to parse the words, and return a chart
    chart = cky(grammar, words)
    print_tree(chart)