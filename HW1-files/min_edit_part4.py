import sys
import re

# this regexp will match any vowel symbol
V = r"[0123456789$@EI{VQUiu#cq]"

### PART 4
# EDIT: finds the index of the first vowel in the word, returns len(word) if no vowel is found
def find_first_vowel(word):
    match = re.search(V, word)
    return match.start() if match else len(word)

# EDIT: higher cost for edits in rime
def ins_cost(c, is_rime):
    return 1 if not is_rime else 2

def del_cost(c, is_rime):
    return 1 if not is_rime else 2

def sub_cost(c, d, is_rime):
    if c == d:
        return 0
    return 2 if not is_rime else 4

def min_edit(source='', target='', verbose=False):
    m = len(source)
    n = len(target)

    # EDIT: find first vowel positions to determine start of rime
    vowel_source = find_first_vowel(source)
    vowel_target = find_first_vowel(target)

    dist = [[0]*(m+1) for i in range(n+1)]

    ## PART 1 - fill in the values of dist using the min_edit algorithm here##
    # Initialization: the zeroth row and column is the distance from the empty string
    dist[0][0] = 0
    #Cost of deleting characters from string
    for i in range(1, n+1):
        is_rime = i - 1 >= vowel_target
        dist[i][0] = dist[i-1][0] + del_cost(target[i-1], is_rime)
    #Cost of inserting characters into empty string
    for j in range(1, m+1):
        is_rime = j - 1 >= vowel_source
        dist[0][j] = dist[0][j-1] + ins_cost(source[j-1], is_rime)
    #Recurrence relation
    # EDIT: applies increased edit costs if in rime
    for i in range(1, n+1):
        for j in range(1, m+1):
            is_rime = (i - 1 >= vowel_target) or (j - 1 >= vowel_source)
            dist[i][j] = min(dist[i-1][j] + del_cost(target[i-1], is_rime),
                            dist[i-1][j-1] + sub_cost(target[i-1], source[j-1], is_rime),
                            dist[i][j-1] + ins_cost(source[j-1], is_rime))


    ## if verbose is set to True, will print out the min_edit table
    if verbose:
        #print the matrix
        for j in range(m+1)[::-1]:
            if j > 0: print(source[j-1], end='')
            else: print('#', end='')
            for i in range(n+1):
                print('\t' + str(dist[i][j]), end='')
            print()
        print('#\t#\t' + '\t'.join(list(target)) + '\n')

    # returns the cost for the full transformation
    return dist[n][m]

def main():
    s = sys.argv[1]
    t = sys.argv[2]
    print(min_edit(source = s, target = t,verbose=True))

if __name__ == "__main__":
    main()
