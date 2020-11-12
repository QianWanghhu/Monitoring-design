"""
This script is used to process the discharge-concentration data.
"""
# import packages
import numpy as np
import pandas as pd
import os
import datetime
# define the repository path
from common_settings import fpath
import matplotlib.pyplot as plt
import seaborn as sns

def subst(x, str_re, loc):
    """
    Parameters:
    -----------
    x :  str, the string to be updated
    str_re :  str, the new string to replace
    loc : int or numpy.array, the index of where to replace x with y

    Returns:
    --------
    x_new : updated new string
    """
    if isinstance(loc, int):
        if loc == -1:
            x_new = x[:loc] + str_re
        else:
            x_new = x[:loc] + str_re + x[loc+1:]
    elif loc[-1] == -1:
        x_new = x[:loc[0]] + str_re
    else:
        x_new = x[:loc[0]] + str_re + x[loc[1]+1:]

    return x_new

# Read discharge (Q) and the concentration (C) data
# Read discharge data
fnames = os.listdir(fpath)
childpath = fpath + '/' + fnames[0] + '/'
fnames = os.listdir(childpath)
discharge = pd.read_csv(childpath + fnames[0])
discharge = discharge.drop(index=[0, 1, 2]).drop(index=[30556, 30557]).\
    filter(items=['Time', '126001A'], axis=1)
discharge['Time'] = pd.to_datetime(discharge['Time'], format="%H:%M:%S %d/%m/%Y")
discharge.set_index(['Time'], inplace=True)

def prep_cq(fnames, index_file, loc, savefile=True):
    """
    Parameters:
    ------------
    fnames : list, list of file names
    index_file : int, the index of file to read
    loc : np.array, location where the string to be replaced
    savefile : Bool, optional, save files if True

    Returns:
    ------------
    files saved to the given directory.
    """
    print(index_file)
    cons_names = [fname.split('-')[-1][:-4] for fname in fnames[1:]]
    print(cons_names)
    concentration = pd.read_csv(childpath + fnames[index_file])
    concentration.rename(columns={concentration.columns[0]: 'Time',
                            concentration.columns[1]: '126001A-' + cons_names[index_file-1] + '(mg/l)'}, inplace=True)
    concentration.drop(index=[0, 1], inplace=True)
    concentration.dropna(how='all', inplace=True, axis=1)

    # Match C-Q data according to time
    """ Assumptions: 1) If there are more than one obs C in an hour, the average of the C is used
    2) the mean of flow
    """
    # if index_file ==4:
    #     import pdb; pdb.set_trace()
    # Convert the string in "Time" to datetime
    if concentration['Time'][2][-2:] == '00':
        concentration['Time'] = concentration['Time'].apply(subst, args=('00', loc[1]))
    else:
        concentration['Time'] = concentration['Time'].apply(subst, args=('00', loc[0]))

    concentration['Time'] = pd.to_datetime(concentration['Time'], format="%Y/%m/%d %H:%M")
    concentration.set_index(['Time'], inplace=True)
    # concentration.drop_duplicates(keep='first', inplace=True)
    cq = pd.concat([concentration, discharge], axis=1, join='inner')
    cq.reset_index(inplace=True)
    cols = cq.columns
    cq.loc[:, cols[1:]] = cq.loc[:, cols[1:]].astype(float)
    cq.rename(columns = {cols[-1] : 'Discharge (meter)'}, inplace=True)

    if savefile:
        cq.to_csv('../output/cq-' + cons_names[index_file-1] + '.csv', index=False)

# set the index for 
loc = [[-2, -1], [-5, -4]]
for i in range(1, len(fnames)):
    prep_cq(fnames, i, loc, savefile=True)

#### TODO #######
# Solve problems with reading duplicates


