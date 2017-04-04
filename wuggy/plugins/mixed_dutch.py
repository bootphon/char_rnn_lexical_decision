# Mixed Dutch
public_name='Mixed Dutch'
default_data='mixed_dutch.txt'
default_neighbor_lexicon='mixed_dutch.txt'
default_word_lexicon='mixed_dutch.txt'
default_lookup_lexicon='mixed_dutch.txt'
hidden_sequence=True
from subsyllabic_common import *
def transform(input_sequence, frequency=1):
    return copy_onc_hidden(input_sequence, frequency=frequency)
