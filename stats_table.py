"""
input_table: words, nonwords and their respective probabilities
corpus_h5: hdf5 file containing the corpus on which the model has been trained
corpus_json: json file containing the vocabulary
ouput_table: input table augmented with spot the word task and additional 
             statistics (such as word frequency in the corpus)
"""
import data_loader
import re
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-input_table")
parser.add_argument("-output_table")
parser.add_argument("-corpus_h5")
parser.add_argument("-corpus_json")
args = parser.parse_args()

table = []

input_table = args.input_table
output_table = args.output_table
corpus_h5 = args.corpus_h5
corpus_json = args.corpus_json

with open(input_table) as f:
    dict_keys = f.readline().rstrip('\n').split('\t')
    for line in f:
        entry = {dict_keys[i]: e.rstrip('\n') for i,e in enumerate(line.split('\t'))}
        table.append(entry)


for entry in table:
    if float(entry['Nonword_Prob']) < float(entry['Word_Prob']):
        entry['Forced_Choice'] = 'Right'
    else:
        entry['Forced_Choice'] = 'Wrong'


# load training, validation and test set
train, val, test = data_loader.load(corpus_h5, corpus_json)
vocab = re.split('\W+', train) # what about the vocabulary of the validation and testing set?
N = len(vocab)
occurences = {}
for word in vocab:
    if word in occurences:
        occurences[word] += 1
    else:
        occurences[word] = 1

def count(word):
    if word in occurences:
        return occurences[word]
    else:
        return 0


current_word = table[0]['Word']
occ = count(current_word)
freq = 1000000*occ/float(N)
for entry in table:
    if entry['Word'] != current_word:
        current_word = entry['Word']
        occ = count(current_word)
        freq = 1000000*float(occ)/N
    entry['Word_Freq'] = str(freq) #frequency per million in the data set
    entry['Word_Occ'] = str(occ)


directory = os.path.dirname(output_table)
if not os.path.exists(directory):
        os.makedirs(directory)

with open(output_table,'w+') as f:
    #columns = ['Word', 'Match', 'Lexicality', 'Forced_Choice', 'Word_Freq', 'Dist', 'Word_Prob', 'Nonword_Prob'] 
    columns = ['Word', 'Match', 'Forced_Choice', 'Word_Prob', 'Nonword_Prob', 'Word_Freq', 'Word_Occ' ] 
    for c in table[0].keys():
        if c not in columns:
            columns.append(c)
    f.write('\t'.join(columns)+'\n')

    lines = [] 
    for entry in table:
        sorted_entry = [entry[c] for c in columns]
        lines.append('\t'.join(sorted_entry))
    f.write('\n'.join(lines))

