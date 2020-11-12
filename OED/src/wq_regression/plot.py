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

# plot the time series of discharge, concentration and C-Q
const_name = 'NO3'
cq = pd.read_csv('../output/cq-' + const_name + '.csv')
cols = cq.columns

sns.set_style('white')
fig, axes = plt.subplots(2, figsize=(8, 10))
sns.scatterplot(data = cq, x = cols[2], y = cols[1], ax=axes[0])
ax1 = cq.plot(x = cols[0], y = cols[2], kind='line', ylim=[0, 7],
    ylabel='Discharge (meter)', ax=axes[1]) #, logy=True
ax2 = ax1.twinx()
cq.plot(x = cols[0], y = cols[1], kind='scatter', ax = ax2, 
        color = 'orange', alpha=0.5, s=1) # ylim=[0, 7],

plt.savefig('../output/figs/cq-' + const_name + '.png', format='png', dpi=300)
