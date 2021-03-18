import pandas as pd
import numpy as np
import os

from utils import generate_obsnme, pre_observation_pst, \
    noise_stats, generate_noise


# IF-ELSE whether to run the model to generate obs for .pts file
fname = '../../data/observation.csv'
if not os.path.exists(fname):
    load = pd.DataFrame()
    import obs_source
else:
    load = pd.read_csv(fname, index_col='Unnamed: 0')
    column_names = load.columns[0]
# End If

# Add noise to the model outputs
std_level = noise_stats(load.values, 0.1)
noise = generate_noise(load.shape[0], dist='normal', pars={'mean':0, 'std': std_level})
load_min = load.loc[:, column_names].min()
noised_obs = load.loc[:, column_names].add(noise)
noised_obs = np.where(noised_obs >= 0, noised_obs, load_min)
load.loc[:, 'noised'] = noised_obs

# Prepare the observation into the format for .pst file
obsval = noised_obs
obgnme = 'DIN'
obs_index = list(load.index)
obsnme = generate_obsnme(obs_index, obgnme)

obs_pst = pre_observation_pst(obsval, obsnme, obgnme)
# obs_pst.weight.format(f'%:.2E')
obs_pst.weight = obs_pst.weight.map('{:,.2E}'.format)
obs_pst.obsval = obs_pst.obsval.map('{:,.3f}'.format)
obs_pst.head()
obs_pst.to_csv('../../data/obs_pst.csv', sep=' ')

## prepare obervation_ensemble
obs_ensemble = pd.read_csv('../../data/din_daily.csv', index_col='Unnamed: 0')
obgnme = 'DIN'
obs_ensemble.index = generate_obsnme(list(obs_ensemble.index), obgnme)
obs_ensemble = obs_ensemble.T
obs_ensemble.reset_index(drop=True, inplace=True)
obs_ensemble.index.name = 'real_name'
obs_ensemble.to_csv('observation_ensemble.csv')

