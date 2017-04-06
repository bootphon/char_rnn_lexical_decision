# Installation

## Basic installation

You will need to install the dependencies of `torch-rnn` from jcjohnson, including 
`torch` and `python 2.7`. You don't need to actually install `torch-rnn`, a slightly 
modified version is already in `networks/`. You will find every detail on the 
github of the project:

https://github.com/jcjohnson/torch-rnn/

Once these requirements are met you should be able to run everything. Slightly 
modified versions of torch-rnn and [Wuggy](http://crr.ugent.be/programs-data/wuggy) are already provided.

**This installation does not provide the corpus we used for our experiments.**

## Downloading the complete data

We trained networks on a corpus crafted from the [BookCorpus dataset](http://yknzhu.wixsite.com/mbweb).
In accordance with their policy, our corpus should only be used for scientific or research 
purposes in academic affiliations.
For accessing our complete data (corpus, trained networks, results...), please send me an email
with your name and affiliation at _gael.le-godais at orange.fr_ 

# Corpus preprocessing

The non processed corpus should be in `corpus/`
The preprocessing has two steps:

* A general preprocessing step that cleans the corpus, splits it and 
  surrounds every word with spaces. The processed corpus should be 
  created in `data/`

* A second processing step dedicated to the training of the neural networks.
  These corpus should be created in `networks/data/` using a corpus that 
  went through the first step.
        

The first processing step takes a corpus in a txt file in input. Splits the 
corpus after `size` characters (0 -> no splitting). Then surrounds every word 
with spaces and writes the resulting corpus in output (meant to be in `data/`):

        python corpus/preprocessing.py -i input -o output [-s size]

The second processing step takes a preprocessed corpus from `data/` in input and
generates a hdf5 and a json files (meant to be created in `networks/data/`):

        python networks/scripts/preprocess.py --input_txt data/my_data.txt \
                                              --output_h5 networks/data/my_data.h5 \
                                              --output_json networks/data/my_data.json

# Nonword generation with Wuggy

We use Wuggy to generate a list of nonwords, where every nonword is a match of 
an actual word. Even though Wuggy is usually used with the GUI, we have to use 
a script here. Some examples of the use of wuggy without GUI can be found in 
wuggy/sequencegenerator/
To generate a list of nonwords matching the list of types from a corpus, we use:

        cd wuggy/sequencegenerator/
        python generation.py -i input -o output
        cd ../../

It extracts a dictionary from the corpus in input and generates a list of nonwords 
matching segment length, total length and transition frequencies in output.
The output as well as the input should be in `data/`. If you had acces to the complete 
data, there are already examples called `data/stimuli*.txt`.

# Training of a neural network and evaluation on the spot-the-word task

`run_network.py` is a wrapper of the following scripts:

        networks/train.lua
        networks/evaluation.lua
        stats_table.py

It trains a neural network, then evaluates its score on a spot-the-word task 
and print a summary of different statistics in a table.

        python run_network.py -model_type               lstm or rnn
                              -rnn_size                 number of hidden units in the network
                              -num_layers               number of layers in the network
                              -number                   numbering of the network (usefull when training multiple instances of the same network)
                              -checkpoint_folder        network save folder (should be networks/cv/)
                              -experiment_name          usefull to name folders in networks/cv/, probs/ and tables/
                              -corpus_h5                output file of networks/scripts/preprocess.py usually in networks/data/
                              -corpus_json              output file of networks/scripts/preprocess.py usually in networks/data/
                              -stimuli                  list of words and their matching nonword (usually in data/)
                              [-no_training]            this option evaluates the network skipping the training (the network should already be trained)

# Running a full experiment

Some shell scripts are provided to run experiments on the cluster using qsub (for LSCP people) or 
directly on the host machine such as `exp500k.sh` or `gen_500k.sh`

# Add baselines to an experiment

Once a full experiment has been run it is possible to add token based unigram 
and bigram language model.

        python baselines.py -stimuli data/nonword_list.txt -h5_corpus networks/data/corpus.h5 \
                            -json_corpus networks/data/corpus.json -dump_folder tables/experiment_name/

# Experiment analysis

An analysis of lexical capacity is provided:

        python lex_capacity.py -tables_dir tables/experiment_name/ \
                               -checkpoints networks/cv/experiment_name/ \
                               -output_file results/results.csv

The output is a tidy data table summing up the parameters of the experiment 
models and their lexical capacity over the given stimulus.

# Miscellaneous

`probs/` might be a bit weird at first because it is redundant with `tables/` but 
with less information. That's because the generation of a result table is done 
in two steps. First the network is evaluated on a list of `words/nonwords` and the 
resulting lexicality indicators are stored in `probs/` folder. Then the second 
step is done with python and adds some statistics to this table. 
