#!/bin/bash

model_types=( 'rnn' 'lstm' )
num_layers=( 1 2 3 )
rnn_sizes=( 16 32 64 128 )
N_times=1

N_types=${#model_types[@]}
N_layers=${#num_layers[@]}
N_sizes=${#rnn_sizes[@]}

for (( n = 0; n < N_times; n++ )); do
	for (( i = 0; i < N_types; i++ )); do
		for (( j = 0; j < N_layers; j++ )); do
			for (( k = 0; k < N_sizes; k++ )); do
				name="${model_types[$i]}_${num_layers[$j]}_${rnn_sizes[$k]}_$n"
                                python run_network.py -no_training -model_type ${model_types[$i]} -rnn_size ${rnn_sizes[$k]} -num_layers ${num_layers[$j]} -number $n -checkpoint_folder networks/cv/exp50M/ -experiment_name gen_exp50M -corpus_h5 networks/data/corpus50M.h5 -corpus_json networks/data/corpus50M.json -stimuli data/generative50M.txt
			done
		done
	done
done
