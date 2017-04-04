import data_loader
import argparse
import numpy as np
import pandas as pd
from pandas.stats.api import ols
import os
import shutil
import subprocess
import re

parser = argparse.ArgumentParser()
parser.add_argument("-tables_dir", default="tables/exp/")
parser.add_argument("-checkpoints", default="networks/cv/")
parser.add_argument("-output_file", default="results/exp1.csv")
args = parser.parse_args()

try:
    os.mkdir(args.tables_dir)
except:
    pass

try:
    os.makedirs(os.path.dirname(args.output_file))
except:
    pass

# first copy all json saves to the output directory
for f in os.listdir(args.checkpoints):
    if f.endswith('json'):
        save = os.path.join(args.checkpoints, f)
        shutil.copy(save,args.tables_dir)

def name_to_key(f):
    if 'type_unigram' in f:
        key = 'type_unigram'
    elif 'unigram' in f:
        key = 'unigram'
    elif 'type_bigram' in f:
        key = 'type_bigram'
    elif 'bigram' in f:
        key = 'bigram'
    else:
        model_type = None
        if 'lstm' in f:
            model_type = 'lstm'
        elif 'rnn' in f:
            model_type = 'rnn'
        hidden_units, num_layers, iter_nb = re.findall('\d+', f)[:3]
        key = (model_type, hidden_units, num_layers, iter_nb)
    return key


results = {}
for filename in os.listdir(args.tables_dir):
    if filename.endswith('txt'):
        f = filename.rstrip('.txt')
        key = name_to_key(f)
        filename = os.path.join(args.tables_dir, filename)

        df = pd.read_csv(filename, sep='\t')
        right_nb = df[df['Forced_Choice'] == 'Right']['Forced_Choice'].count()
        wrong_nb = df[df['Forced_Choice'] == 'Wrong']['Forced_Choice'].count()
        match_per_word = df[['Word','Match']].groupby('Word').count()['Match'].mean()
        words_nb = len(df['Word'].unique())
        N = right_nb + wrong_nb
        n = (2*right_nb - N)/float(match_per_word)

        accuracy = str(100*right_nb/float(N))
        lex_capacity = str(100*n/float(words_nb))
        results[key] = {'accuracy': accuracy, 'lex_capacity': lex_capacity, 'n_parameters': 0, 'loss': 0}

for filename in os.listdir(args.tables_dir):
    if filename.endswith('json'):
        f = filename.rstrip('.json')
        key = name_to_key(f)
        if key in results:
            filename = os.path.join(args.tables_dir, filename)
            results[key]['n_parameters'] = str(data_loader.get_parameters(filename))
            results[key]['loss'] = str(data_loader.get_loss(filename))
        else:
            pass # there is a checkpoint but no corresponding table


#export the results to the tidy data format
def create_tidy_data(file_name):
    lines = []
    lines.append('architecture,units,layers,accuracy,lex_capacity,n_parameters,loss')
    for key in results:
        if isinstance(key, basestring):  #if key is a n-gram 
            line = [key,'NA','NA']
        else:
            line = list(key[:3])
        line.append(results[key]['accuracy'])
        line.append(results[key]['lex_capacity'])
        line.append(results[key]['n_parameters'])
        line.append(results[key]['loss'])
        lines.append(','.join(line))
    table = '\n'.join(lines)
    with open(file_name, 'w+') as f:
        f.write(table)


#print '\nCreating a tidy data summary...'
#output_file = args.output.rstrip('/') + '/' + 'exp1.csv'
create_tidy_data(args.output_file)

