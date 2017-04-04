#encoding: utf-8
from fractions import *
import random

import sys
sys.path.append('../')
from generator import Generator
from plugins import orthographic_english

gty = Generator()
gty.data_path = ('../data')
gty.load(orthographic_english)
gty.load_word_lexicon()
gty.load_neighbor_lexicon()
gty.load_lookup_lexicon()

gto = Generator()
gto.data_path = ('../data')
gto.load(orthographic_english,token=True)
gto.load_word_lexicon()
gto.load_neighbor_lexicon()
gto.load_lookup_lexicon()


words=random.sample(gty.lookup_lexicon,100)
ty_nonwords = []
to_nonwords = []
# err
ncandidates = 1
valid_index = []
nonwords_index = 0

for n, word in enumerate(words):
    #print word.upper()
    gty.set_reference_sequence(gty.lookup(word))
    #gty.set_attribute_filter('sequence_length') 
    gty.set_attribute_filter('segment_length')
    gty.set_statistic('lexicality')
    gty.set_output_mode('plain')

    gto.set_reference_sequence(gto.lookup(word))
    #gto.set_attribute_filter('sequence_length')
    gto.set_attribute_filter('segment_length')
    gto.set_statistic('lexicality')
    gto.set_output_mode('plain')

    jty = 0
    jto = 0
    for i in range(1,10):
        #print ('frequency band: -%d +%d' % (2**i,2**i))
        gty.set_frequency_filter(2**i,2**i)
        gto.set_frequency_filter(2**i,2**i)
        if jty<ncandidates:
            for ty_sequence in gty.generate(clear_cache=False):
                if gty.statistics['lexicality']=='N':
                    #print 'type match:', unicode(ty_sequence)
                    ty_nonwords.append(ty_sequence)
                    jty += 1
                    if jty>=ncandidates:
                        break
        if jto<ncandidates:
            for to_sequence in gto.generate(clear_cache=False):
                if gto.statistics['lexicality']=='N':
                    #print 'token match:', unicode(to_sequence)
                    to_nonwords.append(to_sequence)
                    jto += 1
                    if jto>=ncandidates:
                        break
        if jto>=ncandidates and jty>=ncandidates:
            valid_index.append((n,nonwords_index))
            nonwords_index += 1
            break

lines = ['\t'.join([words[i], ty_nonwords[j], to_nonwords[j]]) for i,j in valid_index]
tab = 'word\ttype match\ttoken match\n' + '\n'.join(lines)

print tab


