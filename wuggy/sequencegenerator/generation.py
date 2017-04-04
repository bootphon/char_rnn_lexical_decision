#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extracts a dictionary from the corpus in input and generates a list of nonwords 
matching segment length, total length and transition frequencies
"""

from fractions import *
import random
import argparse
import re
import sys
sys.path.append('../')
from generator import Generator
from plugins import orthographic_english

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='input_path', help='corpus from which a dictionary will be extracted')
parser.add_argument('-o', dest='output_path', help='output file containing a table of words and matches')
args = parser.parse_args()

#dictionary of the corpus
with open(args.input_path) as f:
    text = f.read()
    words = set(re.findall(r' ([\S]+) ', text))


g = Generator()
g.data_path = ('../data')
g.load(orthographic_english)
g.load_word_lexicon()
g.load_neighbor_lexicon()
g.load_lookup_lexicon()

#words=random.sample(gt.lookup_lexicon,10)
legal_words = g.lookup_lexicon

ncandidates = 1
lines = []
for word in words:
    j = 0
    if word in legal_words:
        g.set_reference_sequence(g.lookup(word))
        for i in range(1,10):
            g.set_frequency_filter(2**i,2**i)
            g.set_attribute_filter('sequence_length') 
            g.set_attribute_filter('segment_length')
            #g.set_all_statistics()
            #g.set_statistic('overlap_ratio')
            g.set_statistic('plain_length')
            g.set_statistic('transition_frequencies')
            g.set_statistic('ned1')
            g.set_statistic('lexicality')
            g.set_output_mode('plain')
            # it's important not to use the cache because we want wuggy to always 
            # generate the best matching nonword. The use of the cache would prevent 
            # to generate multiple times the same nonword and thus lower the quality 
            # the pairs. (and would cause performance issues on big sets of words)
            for sequence in g.generate(clear_cache=True):
                try:
                    sequence.encode('ascii')
                except UnicodeEncodeError:
                    #the matching nonword is non-ascii (bad wuggy)
                    pass
                else:
                    match=False
                    #if (g.statistics['overlap_ratio']==Fraction(2,3) and 
                    #            g.statistics['lexicality']=="N"):
                    if g.statistics['lexicality']=="N":
                        match=True
                    if match:
                        line = []
                        line.append(word)
                        line.append(sequence)
                        # append statistics, doesn't work yet
                        #line.extend(g.statistics.values())
                        #line.extend(g.difference_statistics.values())
                        lines.append('\t'.join(line))
                        j=j+1
                        if j>=ncandidates:
                            break
            if j>=ncandidates:
                break

first_line = '\t'.join(['Word', 'Match']) #+ g.statistics + g.difference_statistics) 
output = first_line + '\n' + '\n'.join(lines)

with open(args.output_path, 'w+') as f:
    f.write(output)
