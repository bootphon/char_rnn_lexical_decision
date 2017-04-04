# Phonetic English
public_name='Phonetic English (CMU)'
default_data='phonetic_english2.txt'
default_neighbor_lexicon='phonetic_english2.txt'
default_word_lexicon='phonetic_english2.txt'
default_lookup_lexicon='phonetic_english2.txt'
hidden_sequence=False
from subsyllabic_common import *
def transform(input_sequence, frequency=1):
    return copy_onc(input_sequence, frequency=frequency)
