"""
Loads the training set, validation set and test set into strings
"""
import h5py
import json
import numpy as np

def load_json(json_file):
    """ load a json file """
    with open(json_file, 'r') as f:
        json_data = json.loads(f.read())
    return json_data

def load(h5_file, json_file):
    """ return the training set, validation set and test set in string format """
    with h5py.File(h5_file, 'r') as hf:
        v_train = np.array(hf.get('train'))
        v_val = np.array(hf.get('val'))
        v_test = np.array(hf.get('test'))
    idx_to_token = load_idx(json_file)
    train = vec_to_str(v_train, idx_to_token)
    val = vec_to_str(v_val, idx_to_token)
    test = vec_to_str(v_test, idx_to_token)
    return train, val, test

def vec_to_str(vec, idx_to_token):
    """ convert vector representation into string """
    l_characters = [idx_to_token[str(idx)] for _, idx in np.ndenumerate(vec)]
    return ''.join(l_characters)

def load_idx(json_file):
    """ load the correspondance table between tokens and ids """
    json_data = load_json(json_file)
    idx_to_token = json_data['idx_to_token']
    return idx_to_token

def get_loss(json_save):
    """ 
    return loss of a network
    json_save: json file of the network
    """
    json_data = load_json(json_save)
    loss = json_data['loss']
    return loss

def get_parameters(json_save):
    """
    return number of parameters of the network
    json_save: json file of the network
    """
    json_data = load_json(json_save)
    n_parameters = json_data['n_parameters']
    return n_parameters
