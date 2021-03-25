"""
The script is used to run commands for OED including the run for parameter,observation ensemble,
adding noise and running IES.
"""
# import packages
import os
import numpy as np
import pandas as pd
from funcs.prep_template import pre_ies_obs_template, format_obs_ensemble, add_noise_obs, generate_obsnme

# format ies inputs
datapath = '../../data/'
fname = f'{datapath}observation.csv'
fname_obs_pst = 'obs_pst_noise10pct.csv'
obgnme = 'DIN'
if not os.path.exists(fname_obs_pst):
    # To CONTINUE: Monthly/annual monitoring as well as introducing noise
    load = pd.read_csv(fname, index_col='Unnamed: 0')
    obs_pst_name = f'{datapath}{fname_obs_pst}'
    load = add_noise_obs(load, noise_level=0.1)
    obs_index = list(load.index)
    obsnme = generate_obsnme(obs_index, obgnme)
    obsval = load.noised.values
    pre_ies_obs_template(obsval, obsnme, obgnme).to_csv(fname_obs_pst, sep=' ')

datapath = '../../data/'
if not os.path.exists(f'observation_ensemble.csv'):
    obs_ensemble = pd.read_csv(f'{datapath}din_daily.csv', index_col='Unnamed: 0')
    obs_ensemble = format_obs_ensemble(obs_ensemble, obgnme)
    obs_ensemble.to_csv(f'observation_ensemble.csv')

# convert the timeseries (monitoring and modeling) to a required temporal scale

