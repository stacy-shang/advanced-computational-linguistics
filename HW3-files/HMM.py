# the A and B matrices as dictionaries
A = {'N':{'N':0.54, 'V':0.23, 'R':0.08, '#':0.15}, 'V':{'N':0.62, 'V':0.17, 'R':0.11, '#':0.10}, 'R':{'N':0.17, 'V':0.68, 'R':0.10, '#':0.05}, '#':{'N':0.7, 'V':0.2, 'R':0.1, '#':0.0}}
#A = {'N':{'N':0.23, 'V':0.54, 'R':0.08, '#':0.15}, 'V':{'N':0.62, 'V':0.17, 'R':0.11, '#':0.10}, 'R':{'N':0.68, 'V':0.17, 'R':0.10, '#':0.05}, '#':{'N':0.1, 'V':0.2, 'R':0.7, '#':0.0}}
B = {'N':{'time':0.98, 'flies':0.015, 'quickly':0.005, '#':0.0}, 'V':{'time':0.33, 'flies':0.64, 'quickly':0.03, '#':0.0}, 'R':{'time':0.01, 'flies':0.01, 'quickly':0.98, '#':0.0}, '#':{'time':0.0, 'flies':0.0, 'quickly':0.0, '#':1.0}}
# Define a new emission matrix B2 for Question 4
B2 = {'N':{'time':0.70, 'flies':0.25, 'quickly':0.05, 'swat':0.0, '#':0.0}, 'V':{'time':0.28, 'flies':0.30, 'quickly':0.02, 'swat':0.10, '#':0.0}, 'R':{'time':0.005, 'flies':0.005, 'quickly':0.99, 'swat':0.0, '#':0.0}, '#':{'time':0.0, 'flies':0.0, 'quickly':0.0, 'swat':0.0, '#':1.0}}

# two data structures you may find useful for mapping between tags and their (arbitrary) indices
tagnum = {"N":0,"V":1,"R":2,"#":3}    #gives index for a given tag
numtag = ['N','V','R','#']   #gives tag for a given index

# def print_table(table, words, ef='%.4f', colwidth=12):
#     tags = A.keys()
#     print(''.ljust(colwidth), end='')
#     for w in words:
#         print(str(w).ljust(colwidth), end='')
#     print()
#     for n in range(len(A.keys())):
#         print(str(numtag[n]).ljust(colwidth), end='')
#         for t in range(len(words)):
#             out = str(table[t][n])
#             if type(table[t][n]) == tuple: 
#                 form=ef+",%s"
#                 out = form % (table[t][n][0], table[t][n][1])
#             elif type(table[t][n]) == float:
#                 out = str(ef % table[t][n])
#             print(out.ljust(colwidth), end='')
#         print()

def print_table(table, words, ef='%.6f', colwidth=12):
    print(''.ljust(colwidth), end='')
    for w in words:
        print(str(w).ljust(colwidth), end='')
    print()

    for n in range(len(numtag)):
        print(str(numtag[n]).ljust(colwidth), end='')
        for t in range(len(words)):
            val = table[t][n]
            if isinstance(val, tuple):
                out = f"{ef % val[0]}, {val[1]}"
            else:  # handle floats for viterbi
                out = ef % val
            print(out.ljust(colwidth), end='')
        print()

def forward(ws, A, B):
    ws = ['#'] + list(ws) + ['#'] # prepend and postpend ‘#’ to test_sequence
    T = len(ws) # T is the length of the resulting test_sequence
    table = [[0.0] * 4 for _ in range(T)] # create table to store results 
    table[0][tagnum['#']] = 1.0 # initialization: set forward probability of ‘#’ at time step 1 to 1 and all others to 0

    for t in range(1, T): # for time step t from 2 to T
        word = ws[t] # current word in sequence
        for tag_j in tagnum: 
            j = tagnum[tag_j]
            table[t][j] = sum(table[t-1][i] * A[numtag[i]][tag_j] * B[tag_j][word] for i in range(len(numtag)))
    print_table(table, ws)  # print the forward probability table
    forward_prob = table[t][-1]
    return(forward_prob) # return the forward probability stored in the last column in the table for the tag ‘#’ 

def viterbi(ws, A, B):
    ws = ['#'] + list(ws) + ['#'] # prepend and postpend ‘#’ to test_sequence
    T = len(ws) # T is the length of the resulting test_sequence
    v = [[(0.0, "")] * 4 for _ in range(T)] # create table to store viterbi probabilities, where each cell stores a tuple of a float (probability for state) and a string (sequence of tags corresponding to probability)
    v[0][tagnum['#']] = (1.0, "#") # initialization: set viterbi probability of ‘#’ at time step 1 to 1 and all others to 0

    for t in range(1, T): # for time step t from 2 to T
        word = ws[t] # current word in sequence
        for tag_j in tagnum:
            j = tagnum[tag_j]  # get index of current tag_j
            
            max_prob = 0.0
            best_prev_index = None

            for i in range(len(numtag)):  # iterate over all previous states
                prev_prob = v[t-1][i][0]  # probability of being in previous state i
                transition_prob = A[numtag[i]][tag_j]  # transition probability from i to j
                emission_prob = B[tag_j][word]  # emission probability of word from j
                
                prob = prev_prob * transition_prob * emission_prob  # compute viterbi probability

                if prob > max_prob:  # keep track of highest probability
                    max_prob = prob
                    best_prev_index = i  # store the index of the best previous state 
            
            if best_prev_index != None:
                v[t][j] = (max_prob, v[t-1][best_prev_index][1] + " " + tag_j)
    
    best_final_index = None
    best_final_prob = 0.0

    for i in range(len(numtag)):  # find best final state
        if v[T-1][i][0] > best_final_prob:
            best_final_prob = v[T-1][i][0]
            best_final_index = i
    best_sequence = v[T-1][best_final_index][1]

    # Print the Viterbi probability table using the existing print_table function
    table = [[v[t][n][0] for n in range(4)] for t in range(T)]  # Extract only probabilities
    print_table(table, ws)
    return best_sequence, best_final_prob

### MAIN CODE GOES HERE ###
seq = ('time','flies','quickly')
print("calculating forward probability of", seq, ":\n", forward(seq, A, B))
print("calculating most likely tags for", seq, ":\n", viterbi(seq, A, B))
seq = ('swat','flies','quickly')
#print("calculating most likely tags for", seq, ":\n", viterbi(seq, A, B2))