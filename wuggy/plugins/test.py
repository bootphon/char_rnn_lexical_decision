# Orthographic English
public_name='All ASCII orthographic english'
default_data='orthographic_english.txt'
default_neighbor_lexicon='orthographic_english.txt'
default_word_lexicon='orthographic_english.txt'
default_lookup_lexicon='orthographic_english.txt'
from subsyllabic_common import *
import orth.en_ascii as language
def transform(input_sequence, frequency=1):
    return pre_transform(input_sequence, frequency=frequency, language=language)
