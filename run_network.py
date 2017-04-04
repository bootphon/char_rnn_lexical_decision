"""
trains a network and evaluates it on a 'spot the word' task
the results are summarized in a table
if -no_training is specified, the training is skipped (given that the 
network has already been trained) 
"""
import re
import argparse
import subprocess
import glob
import os

parser = argparse.ArgumentParser()
parser.add_argument("-model_type", default='lstm')
parser.add_argument("-rnn_size", default='32')
parser.add_argument("-num_layers", default='2')
parser.add_argument("-number", default='0')
parser.add_argument("-checkpoint_folder", default='networks/cv/corpus100k_test/')
parser.add_argument("-experiment_name", default='corpus100k')
parser.add_argument("-corpus_h5", default='networks/data/corpus100k.h5')
parser.add_argument("-corpus_json", default='networks/data/corpus100k.json')
parser.add_argument("-stimuli", default='data/stimuli100k.txt')
parser.add_argument("-no_training", action='store_true')
args = parser.parse_args()

os.chdir('networks/')

net_id = '_'.join([args.model_type, args.rnn_size, args.num_layers, args.number])
probs_folder = '../probs/' + args.experiment_name + '/'

checkpoint_name = args.checkpoint_folder.rstrip('/') + '/' + net_id
checkpoint_name = checkpoint_name.replace('networks/','')
input_h5 = args.corpus_h5.replace('networks/','')
input_json = args.corpus_json.replace('networks/','')

# training the network
if not args.no_training:
    print 'Training a {} of {} hidden layers of {} units...'.format(args.model_type, args.num_layers, args.rnn_size)
    subprocess.call(['th', 'train.lua', 
        '-input_h5', input_h5, 
        '-input_json', input_json, 
        '-model_type', args.model_type, 
        '-rnn_size', args.rnn_size, 
        '-num_layers', args.num_layers, 
        '-checkpoint_name', checkpoint_name])
    
# evaluation of the network
try:
    os.mkdir(os.path.basename(probs_folder))
except:
    pass
checkpoint = glob.glob(checkpoint_name+'_*.t7')[0]
print '\nEvaluation of a {} of {} hidden layers of {} units...'.format(args.model_type, args.num_layers, args.rnn_size)
subprocess.call(['th', 'word-evaluation.lua', 
    '-checkpoint', checkpoint, 
    '-output_path', probs_folder, 
    '-stimuli', '../'+args.stimuli])

# spot the word task summary in a table
os.chdir('..')

print '\nCreation of table_{}.txt...'.format(net_id)
input_table = 'probs/' + args.experiment_name + '/' + net_id + '.txt'
output_table = 'tables/{}/{}.txt'.format(args.experiment_name, net_id)
try:
    os.mkdir(os.path.dirname(output_table))
except:
    pass
subprocess.call(['python', 'stats_table.py', 
    '-input_table', input_table, 
    '-output_table', output_table,
    '-corpus_h5', args.corpus_h5, 
    '-corpus_json', args.corpus_json])
