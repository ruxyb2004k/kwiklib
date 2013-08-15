"""This module provides functions used to load params files."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import json
import os
import tables
import time

import numpy as np
import matplotlib.pyplot as plt

from klustersloader import (find_filenames, find_index, read_xml,
    filename_to_triplet, triplet_to_filename, find_indices,
    find_hdf5_filenames,
    read_clusters, read_cluster_info, read_group_info,)
from tools import MemMappedText, MemMappedBinary


# -----------------------------------------------------------------------------
# Probe file functions
# -----------------------------------------------------------------------------
def paramsxml_to_json(metadata_xml):
    """Convert PARAMS from XML to JSON."""
    shanks = metadata_xml['shanks']
    params = dict(
        SAMPLING_FREQUENCY=metadata_xml['freq'],
        FETDIM={shank: metadata_xml[shank]['fetdim'] 
            for shank in shanks},
        WAVEFORMS_NSAMPLES={shank: metadata_xml[shank]['nsamples'] 
            for shank in shanks},
    )
    return json.dumps(params, indent=4)

def paramspy_to_json(metadata_py):
    """metadata_py is a string containing Python code where each line is
    VARNAME = VALUE"""
    metadata = {}
    exec metadata_py in {}, metadata
    return json.dumps(metadata)


# -----------------------------------------------------------------------------
# Probe parse functions
# -----------------------------------------------------------------------------
def get_freq(params):
    # Kwik format.
    if 'SAMPLING_FREQUENCY' in params:
        return float(params['SAMPLING_FREQUENCY'])
    # Or SpikeDetekt format.
    else:
        return float(params['SAMPLERATE'])

def get_nsamples(params, freq):
    # Kwik format.
    if 'WAVEFORMS_NSAMPLES' in params:
        # First case: it's a dict channel: nsamples.
        if isinstance(params['WAVEFORMS_NSAMPLES'], dict):
            return {int(key): value 
                for key, value in params['WAVEFORMS_NSAMPLES'].iteritems()}
        # Second case: it's a single value, the same nsamples for all channels.
        else:
            return int(params['WAVEFORMS_NSAMPLES'])
    # or SpikeDetekt format.
    else:
        return int(freq * (float(params['T_BEFORE']) + float(params['T_AFTER'])))

def get_fetdim(params):
    # Kwik format.
    if 'FETDIM' in params:
        if isinstance(params['FETDIM'], dict):
            return {int(key): value 
                for key, value in params['FETDIM'].iteritems()}
        else:
            return int(params['FETDIM'])
    # or SpikeDetekt format.
    else:
        return params['FPC']
        
def get_raw_data_files(params):
    return params.get('RAW_DATA_FILES', [])
        
def load_params_json(params_json):
    if not params_json:
        return None
    params_dict = json.loads(params_json)
    
    params = {}
    params['freq'] = get_freq(params_dict)
    params['nsamples'] = get_nsamples(params_dict, params['freq'])
    params['fetdim'] = get_fetdim(params_dict)
    params['raw_data_files'] = get_raw_data_files(params_dict)
    
    return params
    
def load_prm(prm_filename):
    with open(prm_filename, 'r') as f:
        params_text = f.read()
    # First possibility: the PRM is in Python.
    try:
        params_json = paramspy_to_json(params_text)
    # Otherwise, it is already in JSON.
    except:
        params_json = params_text
    # Parse the JSON parameters file.
    params = load_params_json(params_json)
    return params
    
