import numpy as np
import pandas as pd

# read observations 
filenames = ['observation_ensemble', '112101B_observations']
obs_ens = pd.read_csv(f'{filenames[0]}.csv', index_col='real_name').T
obs = pd.read_csv(f'{filenames[1]}.csv', index_col='Date')

# Select a short time period
time_period = ['1/07/2016', '30/06/2018']
obs = obs.loc[time_period[0] : time_period[1], :]

time_period_ens = ['1_07_2016', '30_06_2018']
obs_ens = pd.concat(
            [obs_ens.iloc[0:3], 
            obs_ens.loc['TSS_' + time_period_ens[0] : 'TSS_' + time_period_ens[1], :],
            obs_ens.loc['PN_' + time_period_ens[0] : 'PN_' + time_period_ens[1], :],
            obs_ens.loc['PP_' + time_period_ens[0] : 'PP_' + time_period_ens[1], :]]
            )
            
obs_ens = obs_ens.T            
obs.to_csv(filenames[1] + '.csv', index=True)
obs_ens.to_csv(filenames[0] + '.csv', index=True)

pstfile = np.loadtxt('112101B.txt')