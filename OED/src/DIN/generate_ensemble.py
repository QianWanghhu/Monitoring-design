"""
The script is used to generate the parameter and data ensemble.
The parameters are generated with Sobol' sampling or LHS.
"""
import numpy as np
import pandas as pd
import SALib
from SALib.sample import latin
import sobol_seq

datapath = '../../data/'
parameters = pd.read_csv(datapath + 'Parameters.csv', index_col = 'Index')
parameters

problem = {
    'num_vars': parameters.shape[0],
    'names': parameters.Name_short.values,
    'bounds': parameters.loc[:, ['Min', 'Max']].values
}

parameters_ensemble = latin.sample(problem, 512, seed=88)

df = pd.DataFrame(data=parameters_ensemble, index = np.arange(512), columns=problem['names'])
df.index.name = 'real_name'
df.to_csv('parameter_ensemble.csv')
