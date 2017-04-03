#!/bin/bash

model_types=( 'rnn' 'lstm' )
num_layers=( 1 2 3 )
rnn_sizes=( 16 32 64 128 )
N_times=5

N_types=${#model_types[@]}
N_layers=${#num_layers[@]}
N_sizes=${#rnn_sizes[@]}

for (( n = 0; n < N_times; n++ )); do
	for (( i = 0; i < N_types; i++ )); do
		for (( j = 0; j < N_layers; j++ )); do
			for (( k = 0; k < N_sizes; k++ )); do
				name="${model_types[$i]}_${num_layers[$j]}_${rnn_sizes[$k]}_$n"
				echo "source /home/glegodais/.bashrc; export OMP_NUM_THREADS=1; export MKL_NUM_THREADS=1; python run_network.py -model_type ${model_types[$i]} -rnn_size ${rnn_sizes[$k]} -num_layers ${num_layers[$j]} -number $n -checkpoint_folder networks/cv/exp5M/ -experiment_name exp5M -corpus_h5 networks/data/corpus5M.h5 -corpus_json networks/data/corpus5M.json -stimuli data/stimuli5M.txt" | qsub -cwd -j yes -S /bin/bash -N $name -pe openmpi_ib 4
			done
		done
	done
done
