"""
Compute the baselines on tokens
Warning: needs refactoring in order to include baselines on types
"""
import re
import data_loader
import json
import os
import numpy as np
import pandas as pd
import argparse
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

parser = argparse.ArgumentParser()
parser.add_argument("-stimuli", default='data/stimuli100k.txt')
parser.add_argument("-h5_corpus")
parser.add_argument("-json_corpus")
parser.add_argument("-dump_folder")
args = parser.parse_args()

try:
    os.mkdir(args.dump_folder)
except:
    pass

#model construction
train, val, test = data_loader.load(args.h5_corpus, args.json_corpus)

N = len(train)

print 'Constructing unigrams...'
uni_vocab = {c for c in train}
uni_occurences = {c:0 for c in uni_vocab}
for c in train:
    uni_occurences[c] += 1
unigrams = {c:float(uni_occurences[c])/N for c in uni_vocab}

def uni_prob(word):
    w = ' ' + word + ' '
    return np.prod([unigrams[c] for c in w])

print 'Constructing bigrams...'
bi_vocab = {train[i:i+2] for i in range(N-1)}
bi_occurences = {cc:0 for cc in bi_vocab}
for cc in [train[i:i+2] for i in range(N-1)]:
    bi_occurences[cc] += 1
bigrams = {cc:float(bi_occurences[cc])/N for cc in bi_vocab}

def bi_prob(word):
    w = ' ' + word + ' '
    l = []
    l.append(unigrams[w[0]])
    for cc in [w[i:i+2] for i in range(0,len(w)-2)]:
        c = cc[0]
        if cc in bigrams:
            l.append(bigrams[cc]/unigrams[c])
        else:
            return 0 #a bigram is not in the corpus
    return np.prod(l)


#model evaluation
def cross_entropy(model, test_corpus):
    def loss(current_c, next_c, model):
        if model == unigrams:
            # some unigrams may be in the validation but not in the training
            if next_c not in unigrams:
                unigrams[next_c] = 0
            loss = -unigrams[next_c] + np.log(sum(np.exp(unigrams.values())))
        elif model == bigrams:
            possible_bigrams = [b for b in bigrams if b[0]==current_c]
            current_bigram = current_c + next_c
            # some bigrams may be in the validation but not in the training
            if current_bigram not in bigrams:
                bigrams[current_bigram] = 0
            loss = -bigrams[current_bigram]/unigrams[current_c]+ np.log(sum([np.exp(bigrams[b]/unigrams[current_c]) for b in possible_bigrams]))
        return loss

    test_set = [(test_corpus[i], test_corpus[i+1]) for i in range(len(test_corpus)/10)]
    avg_loss = 0
    losses = []
    for current_c, next_c in test_set:
        losses.append(loss(current_c, next_c, model))
    avg_loss = sum(losses)/len(losses)
    return avg_loss


# write json files with losses and number of parameters
unigram_file = args.dump_folder.rstrip('/') + '/' + 'unigram.json'
bigram_file = args.dump_folder.rstrip('/') + '/' + 'bigram.json'
with open(unigram_file, 'w') as f:
    dump = {'loss':cross_entropy(unigrams,val), 'n_parameters':len(uni_vocab)}
    json.dump(dump,f)
with open(bigram_file, 'w') as f:
    dump = {'loss':cross_entropy(bigrams,val), 'n_parameters':len(uni_vocab)**2}
    json.dump(dump,f)

# write tables with results of spot the word
print 'Creation of unigram_table.txt...'
unigram_table_file = args.dump_folder.rstrip('/') + '/' + 'unigram_table.txt'
df = pd.read_csv(args.stimuli, sep='\t')
vocab = re.split('\W+',train)
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

df['Word_Occ'] = df['Word'].apply(count)
df['Word_Freq'] = 1000000*df['Word_Occ']/float(N)
df = df[df['Word_Occ'] != 0]

df['Word_Prob'] = df['Word'].apply(uni_prob)
df['Nonword_Prob'] = df['Match'].apply(uni_prob)
df['Forced_Choice'] = ['Right' if df['Word_Prob'][i] > df['Nonword_Prob'][i] else'Wrong' for i in df.index]
df.to_csv(unigram_table_file, sep='\t', index=False)

print 'Creation of bigram_table.txt...'
bigram_table_file = args.dump_folder.rstrip('/') + '/' + 'bigram_table.txt'
df['Word_Prob'] = df['Word'].apply(bi_prob)
df['Nonword_Prob'] = df['Match'].apply(bi_prob)
df['Forced_Choice'] = ['Right' if df['Word_Prob'][i] > df['Nonword_Prob'][i] else'Wrong' for i in df.index]
df.to_csv(bigram_table_file, sep='\t', index=False)

