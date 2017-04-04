"""
Creates a list of stimuli that are not in a given corpus. 

bigger_stimuli: stimuli file
smaller_stimuli: list of stimuli included in the big_stimuli file
                should contain all the word from the corpus
output_stimuli: big_stimuli - little_stimuli
"""

import argparse
import re
import csv

parser = argparse.ArgumentParser()
parser.add_argument('-bigger_stimuli')
parser.add_argument('-smaller_stimuli')
parser.add_argument('-output_stimuli')
args = parser.parse_args()

big_pairs = {}
with open(args.bigger_stimuli) as csv_file:
    reader = csv.reader(csv_file, delimiter='\t')
    first_line = next(reader)
    for row in reader:
        big_pairs[row[0]] = row[1]

small_pairs = {}
with open(args.smaller_stimuli) as csv_file:
    reader = csv.reader(csv_file, delimiter='\t')
    first_line = next(reader)
    for row in reader:
        small_pairs[row[0]] = row[1]

new_pairs = {}
for w in big_pairs:
    if w not in small_pairs:
        new_pairs[w] = big_pairs[w]

with open(args.output_stimuli, 'w') as csv_file:
    writer = csv.writer(csv_file, delimiter='\t')
    writer.writerow(first_line)
    for w, nw in new_pairs.iteritems():
        writer.writerow([w,nw])

