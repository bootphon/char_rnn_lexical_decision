"""
Creates a list of stimuli for a given corpus. 
We suppose here that a list of stimuli has already been produced by Wuggy and 
we want another list for a subset of the original corpus. It is faster than 
using Wuggy once again and guaranties to have the same nonwords. 

input_stimuli: original stimuli file
corpus: new corpus
output_stimuli: new stimuli file
"""

import argparse
import re
import csv

parser = argparse.ArgumentParser()
parser.add_argument('-input_stimuli')
parser.add_argument('-corpus')
parser.add_argument('-output_stimuli')
args = parser.parse_args()

with open(args.corpus) as f:
    text = f.read()
    new_words = set(re.findall(r' ([a-z]+) ', text))

old_pairs = {}
with open(args.input_stimuli) as csv_file:
    reader = csv.reader(csv_file, delimiter='\t')
    first_line = next(reader)
    for row in reader:
        old_pairs[row[0]] = row[1]

new_pairs = {}
for w in new_words:
    if w in old_pairs:
        new_pairs[w] = old_pairs[w]

with open(args.output_stimuli, 'w') as csv_file:
    writer = csv.writer(csv_file, delimiter='\t')
    writer.writerow(first_line)
    for w, nw in new_pairs.iteritems():
        writer.writerow([w,nw])

