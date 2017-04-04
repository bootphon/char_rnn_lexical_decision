#encoding: utf-8
from fractions import *
import random

import sys
sys.path.append('../')
# sys.path.append('../..')
from generator import Generator
from plugins import orthographic_english #subsyllabic_dutch, subsyllabic_english, subsyllabic_french, subsyllabic_basque

g=Generator()
g.data_path=('../data')
#g.load(subsyllabic_basque)
g.load(orthographic_english,token=True)
g.load(orthographic_english)
g.load_word_lexicon()
g.load_neighbor_lexicon()
g.load_lookup_lexicon()
# g.load(subsyllabic_french)
# g.load(subsyllabic_dutch)
# print g.list_output_modes()
# print g.list_statistics()

words=random.sample(g.lookup_lexicon,50)
# err
ncandidates=1
for word in words:
    print word.upper()
    g.set_reference_sequence(g.lookup(word))
    #print g.lookup(word).upper()
    #print g.get_limit_frequencies(['segment_length','sequence_length'])
    # print g.reference_sequence
    g.set_attribute_filter('sequence_length')
    g.set_attribute_filter('segment_length')
    #g.set_statistic('overlap_ratio')
    #g.set_statistic('plain_length')
    #g.set_statistic('transition_frequencies')
    g.set_statistic('lexicality')
    #g.set_statistic('ned1')
    #g.set_output_mode('syllabic')
    g.set_output_mode('plain')
    j=0
    for i in range(1,10):
        #print ('frequency band: -%d +%d' % (2**i,2**i))
        g.set_frequency_filter(2**i,2**i)
        for sequence in g.generate(clear_cache=False):
            match=False
            #if (g.statistics['overlap_ratio']==Fraction(2,3) and 
            #            g.statistics['lexicality']=="N"):
            if g.statistics['lexicality']=="N":
                match=True
            if match==True:
                print unicode(sequence)
                # print g.statistics
                # print g.difference_statistics
                # print ' '.join("%s:%s" % (key,value) for key, value in g.statisticg.iteritems())
                # print ' '.join("%s:%s" % (key,value) for key, value in g.difference_statisticg.iteritems())
                # print ' '.join("%s:%s" % (key,value) for key, value in g.match_statisticg.iteritems())
                j=j+1
                if j>=ncandidates:
                    break
        if j>=ncandidates:
            break
    print 
