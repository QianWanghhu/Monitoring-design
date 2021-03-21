"""
The script is used to run commands for OED including the run for parameter,observation ensemble,
adding noise and running IES.
"""
# import packages
import os
import numpy as np
import pandas as pd
from funcs.prep_template import pre_ies_obs_template, format_obs_ensemble

# format ies inputs
datapath = 'data/'
fname = f'{datapath}observation.csv'
if not os.path.exists(fname):    
    load = pd.read_csv(fname, index_col='Unnamed: 0')
    obs_pst_name = f'{datapath}obs_pst.csv'
    pre_ies_obs_template(load).to_csv(obs_pst_name, sep=' ')

src_path = 'src/DIN/'
if not os.path.exists(f'{src_path}observation_ensemble.csv'):
    obs_ensemble = pd.read_csv(f'{datapath}din_daily.csv', index_col='Unnamed: 0')
    obs_ensemble = format_obs_ensemble(obs_ensemble)
    obs_ensemble.to_csv(f'{src_path}observation_ensemble.csv')

## import and run run_daily_observed
print('All data has been prepared for ies and is going to run run_daily_observed.py')
import run_daily_observed
