# Mixed French
public_name='Mixed French'
default_data='mixed_french.txt'
default_neighbor_lexicon='mixed_french.txt'
default_word_lexicon='mixed_french.txt'
default_lookup_lexicon='mixed_french.txt'
hidden_sequence=True
from subsyllabic_common import *
def transform(input_sequence, frequency=1):
    return copy_onc_hidden(input_sequence, frequency=frequency)
