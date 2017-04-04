#encoding: utf-8
# Given a set of letters, find legal words and pseudowords matching a particular structure

from fractions import *
import random
import codecs
from collections import OrderedDict


import sys
sys.path.append('../')
from generator import Generator
from plugins import subsyllabic_dutch

def onc_skeleton(oncrep):
    pass

def body_rhyme(onc):
    segments=onc.split('.')
    br=[]
    for i in range(len(segments)/3):
        print i
        sylnum=i
        br.append(segments[0+(sylnum*3)])
        br.append(segments[1+(sylnum*3)]+[2+(sylnum*3)])
    return '.'.join(br)

# print body_rhyme('w.e.rk.p.aa.rd')

# err
g=Generator()
g.data_path=('../data')
zdl=codecs.open("%s/zwijsen_dutch_lexicon.txt" % g.data_path,'r','utf-8')

g.load(subsyllabic_dutch, data_file=zdl)
g.load_word_lexicon()
g.load_neighbor_lexicon()
g.load_lookup_lexicon()

# add phonological layer

# add scoring algorithm

# add morphological information, phonology, syllabic information, mkm
# structuur, syntactische klasse, frequenties, body, rhyme, onset, nucleus, coda
# (onset coda skelet) e.g., OCC

ncandidates=-1  # no limit



structure2word={
    'km': 'ik',
    'mkm': 'kim',
    'kkm': 'aap',
    'mkkm': 'raak',
    'mkk': 'zee',
}

level_order=['opening', 'kern 1', 'kern 2', 'kern 3', 'kern 4', 'kern 5', 'kern 6']

# letters sequentieel bijvoegen (kolom met nieuwe letters en nieuwe woorden op basis van deze letter)

# wanneer zak geintroduceerd wordt staat a voor korte a en mogen dus geen woorden met open lettergreep a gegenereerd worden 

# analyseprogramma 

# plakken uit incopy in excel

# schroten en vermeer

levels={
    'opening':{ 'structures': ('km','mkm','mkk'), 
                'segments': ('i','k','m','s')},
    'kern 1':{ 'structures': ('km','mkm','kkm','mkkm'), 
                'segments': ('i','k','m','s','p','aa','r','e','v')},
    'kern 2':{ 'structures': ('km','mkm','kkm','mkkm'), 
                'segments': ('i','k','m','s','p','aa','r','e','v','n','t','ee','b','oo')},
    'kern 3':{ 'structures': ('km','mkm','kkm','mkkm', 'mkk'), 
                'segments': ('i','k','m','s','p','aa','r','e','v','n','t','ee','b','oo','d','oe','z','ij','h')},
    'kern 4':{ 'structures': ('km','mkm','kkm','mkkm', 'mkk'), 
                'segments': ('i','k','m','s','p','aa','r','e','v','n','t','ee','b','oo','d','oe','z','ij','h','w','o','a','u','j')},
    'kern 5':{ 'structures': ('km','mkm','kkm','mkkm'), 
                'segments': ('i','k','m','s','p','aa','r','e','v','n','t','ee','b','oo','d','oe','z','ij',
                'h','w','o','a','u','j','eu','ie','l','ou','uu')},
    'kern 6':{ 'structures': ('km','mkm','kkm','mkkm'), 
                'segments': ('i','k','m','s','p','aa','r','e','v','n','t','ee','b','oo','d','oe','z','ij',
                'h','w','o','a','u','j','eu','ie','l','ou','uu','g','au','ui','f','ei')},
}




for level in level_order:
    for structure in levels[level]['structures']:
        g.set_reference_sequence(structure2word[structure])
        g.set_attribute_filters(['segment_length'])
        g.set_segmentset_filter(set(levels[level]['segments']))
        # g.set_statistic('overlap_ratio')
        g.set_statistic('lexicality')
        g.set_output_mode('subsyllabic')
        for sequence in g.generate(clear_cache=True):
            spelling=unicode(sequence).replace(u'.',u'')
            onc=unicode(sequence)
            lexicality=g.statistics['lexicality']
            if lexicality=='W' and not spelling.endswith('i'):
                # used_set=':'.join(list(set(spelling.replace('-',''))))
                # set_pct=Fraction(len(set(spelling.replace('-',''))),len(set(segments)))
                # print(u"%s\t%s\t%s\t%s\t%s\t%s" % (letterset, structure, spelling, used_set, set_pct, '****' if lexicality=="W" else "----")) 
                print(u"%s\t%s\t%s\t%s\t%s" % (level, structure.upper(), spelling, onc,'****' if lexicality=="W" else "----")) 

        # except:
        #     print 'link error'
        #     