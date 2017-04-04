#encoding: utf-8
from fractions import *
import random
import codecs

import sys
sys.path.append('../')
from generator import Generator
from plugins import mixed_french

g=Generator()
g.data_path=('../data')
g.load(mixed_french)
g.load_word_lexicon()
g.load_neighbor_lexicon()
g.load_lookup_lexicon()

words=g.lookup_lexicon

ncandidates=-1  # no limit

f_out=codecs.open('french_pseudohomophones.txt','w','utf-8')
headers=['base.spelling','base.spelling.onc','base.phonology.onc',
'match.spelling','match.spelling.onc','match.lexicality']
f_out.write(u'\t'.join(headers)+u'\n')
for word in words:
    g.set_reference_sequence(g.lookup(word))
    spelling=word
    onc_spelling, onc_phonology=g.lookup(word).split(u'|')
    g.set_attribute_filter('hidden')
    g.set_statistic('overlap_ratio')
    g.set_statistic('lexicality')
    g.set_output_mode('subsyllabic')
    # it's important not to use the cache because we want wuggy to always 
    # generate the best matching nonword. The use of the cache would prevent 
    # to generate multiple times the same nonword and thus lower the quality 
    # the pairs. (and would cause performance issues on big sets of words)
    for sequence in g.generate(clear_cache=True):
        match_spelling=unicode(sequence).replace(u'.',u'')
        match_spelling_onc=unicode(sequence).replace(u'.',u':')
        match_lexicality='H' if match_spelling==spelling else g.statistics['lexicality']
        f_out.write(u"%s\t%s\t%s\t%s\t%s\t%s\n" % (spelling, onc_spelling, onc_phonology, match_spelling,
        match_spelling_onc, match_lexicality)) 
