import sys
import random
import math

def mel(hertz):
    return(2595 * math.log10(1 + hertz / 700))

voweldata = sys.argv[1]

k = int(sys.argv[2]) # k = desired number of clusters
if len(sys.argv) == 4: # check if optional intitialization file exists
    initialization_file = sys.argv[3]
    means_list = []
    for line in open(initialization_file):
        row = line.split()
        f1_mean = mel(float(row[0]))
        f2_mean = mel(float(row[1]))
        centroid = (f1_mean, f2_mean)
        means_list.append(centroid)

else:
    # FIND MIN AND MAX VALUES FOR F1 AND F2:
    # initialize empty lists to store f1 and f2 values
    # loop thru every line in voweldata file and append values to respective lists
    # find min/max for each list
    f1_values = []
    f2_values = []
    
    for line in open(voweldata):
        if line.strip() == '': break # remove leading/trailing whitespace from sentence, break if encounters empty string
        row = line.split()
        f1 = mel(float(row[4]))
        f1_values.append(f1)
        f2 = mel(float(row[5]))
        f2_values.append(f2)
    
    f1_min = min(f1_values)
    f1_max = max(f1_values)
    f2_min = min(f2_values)
    f2_max = max(f2_values)

    # INITIALIZE K RANDOM MEANS:
    # generate random f1 and f2 in their respective ranges
    # structure is a nested list with centroids as tuples (f1, f2)
    means_list = []
    for i in range(k):
        f1_mean = random.uniform(f1_min, f1_max)
        f2_mean = random.uniform(f2_min, f2_max)
        centroid = (f1_mean, f2_mean)
        means_list.append(centroid)

# GENERATE CLUSTERS
while True:
    clusters = {}
    for line in open(voweldata): # loop thru each data pt in vowel data
        if line.strip() == '': break # remove leading/trailing whitespace from sentence, break if encounters empty string
        row = line.split() # splits row into list for grabbing f1 and f2
        f1_curr = mel(float(row[4])) # grab f1 of token
        f2_curr = mel(float(row[5])) # grab f2 of token
        curr_token = [f1_curr, f2_curr] # put into list format [f1, f2] for dist calc
        distance_dict = {} # make dict of in which keys are centroids and values are distances of token from centroid
        for centroid in means_list: # loop thru each centroid in means list
            distance = math.dist(curr_token, centroid) # calc euclidean dist btwn data pt and centroid
            distance_dict[tuple(centroid)] = distance # add centroid and distance to distance dict
        min_distance = min(distance_dict.values()) # find smallest distance from a centroid
        
        # HANDLE EQUIDISTANCE
        centroids_with_min_dist = [] # list of centroids that have min dist
        for centroid, distance in distance_dict.items():
            if min_distance == distance:
                centroids_with_min_dist.append(centroid) # append centroids to list if their distance is equal to min dist
        centroid = random.choice(centroids_with_min_dist) # pick a random centroid
        # add centroid and corresponding tokens to cluster dict
        if centroid not in clusters:
            clusters[centroid] = [tuple(curr_token)]
        else:
            clusters[centroid].append(tuple(curr_token))

    # GENERATE NEW MEANS
    new_means_list = [] # list of new means to compare to prev list
    for centroid in clusters:
        # initialize f1 and f2 lists to calc mean for each centroid
        centroid_f1_values = []
        centroid_f2_values = []
        for token in clusters[centroid]:
            f1, f2 = token[0], token[1]
            centroid_f1_values.append(f1)
            centroid_f2_values.append(f2)
        centroid_f1_mean = sum(centroid_f1_values) / len(centroid_f1_values)
        centroid_f2_mean = sum(centroid_f2_values) / len(centroid_f2_values)
        new_centroid = (centroid_f1_mean, centroid_f2_mean)
        new_means_list.append(new_centroid)

    # CONVERGENCE
    if means_list == new_means_list:
        # for mean in means_list:
        #     print(f'{mean[0]}       {mean[1]}')
        break
    else:
        means_list = new_means_list

# CALCULATE PRECISION RECALL FSCORE
vowel_dict = {}
for line in open(voweldata):
        if line.strip() == '': break # remove leading/trailing whitespace from sentence, break if encounters empty string
        row = line.split()
        vowel_id = int(row[2])
        f1 = mel(float(row[4]))
        f2 = mel(float(row[5]))
        voweldata_token = (f1, f2)
        vowel_dict[voweldata_token] = vowel_id

reversed_clusters = {}
for centroid in clusters:
    for token in clusters[centroid]:
        reversed_clusters[token] = centroid

true_positives = 0
false_positives = 0
true_negatives = 0
false_negatives = 0

tokens = list(vowel_dict.keys())
n = len(tokens)

for i in range(n):
    for j in range(i+1, n):
        v1 = tokens[i]
        v2 = tokens[j]

        v1_cluster = reversed_clusters[v1]
        v2_cluster = reversed_clusters[v2]

        v1_vowel = vowel_dict[v1]
        v2_vowel = vowel_dict[v2]

        if v1_cluster == v2_cluster and v1_vowel == v2_vowel:
                true_positives += 1
        elif v1_cluster == v2_cluster and v1_vowel != v2_vowel:
                false_positives += 1
        elif v1_cluster != v2_cluster and v1_vowel != v2_vowel:
                true_negatives += 1
        elif v1_cluster != v2_cluster and v1_vowel == v2_vowel:
                false_negatives += 1

precision = true_positives / (true_positives + false_positives)
recall = true_positives / (true_positives + false_negatives)
f_score = (2*precision*recall) / (precision+recall)

print(f'Precision: {precision}')
print(f'Recall: {recall}')
print(f'F-score: {f_score}')