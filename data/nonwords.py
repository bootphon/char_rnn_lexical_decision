"""
Takes in input: - a csv file of words and matching non words
                - a corpus
Every word in the corpus should be in the csv file.
Words are extracted from the corpus and a csv file containing words and their 
matching nonwords is created.
This is a lot faster than generating nonwords with wuggy again
"""

import csv
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-full_stimuli', default='full-stimuli.txt')
parser.add_argument('-corpus')
parser.add_argument('-output_stimuli')
args = parser.parse_args()

with open(args.corpus, 'r') as f:
    text = f.read()
    corpus_words = set(re.split(r'\s', text))

output_rows = []
with open(args.full_stimuli, 'r') as f:
    first_row = True
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        if first_row:
            output_rows.append(row)
            first_row = False
        if row[0] in corpus_words:
            output_rows.append(row)

with open(args.output_stimuli, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    for row in output_rows:
        writer.writerow(row)





