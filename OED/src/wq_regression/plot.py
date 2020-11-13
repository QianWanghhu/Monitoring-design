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


def cq_line_plot(df, ylabel_str, logy=False, ax=None):
    """
    df : dataframe, dataframe to plot, contains the time as the first column
    ylabel : str, str to set as the y-axis label
    logy : Bool, optional. If True, the first y axis will be displayed in log scale
    """
    sns.set_style('white')
    ax1 = df.plot(x = cols[0], y = cols[2], kind = 'line', ylim = [0, 7],
        ylabel = ylabel_str, logy = logy, ax = ax) #
    ax2 = ax1.twinx()
    df.plot(x = cols[0], y = cols[1], kind = 'scatter', ax = ax2, 
            color = 'orange', alpha = 0.5, s = 1)

# plot the time series of discharge, concentration and C-Q
const_name = 'NO3'
cq = pd.read_csv('../../output/cq-' + const_name + '.csv')
cq.Time = pd.to_datetime(cq.Time)
for i in range(cq.shape[0]):
    cq.loc[i, 'index'] = cq.Time[i].strftime("%Y-%m-%d")
cq.set_index('index', inplace=True)
cols = cq.columns

# Plot
sns.set_style('white')
ylabel_str = 'Discharge (meter)'
fig, axes = plt.subplots(2, figsize=(8, 10))
sns.scatterplot(data = cq, x = cols[2], y = cols[1], ax=axes[0])
cq_line_plot(cq, ylabel_str, logy=False, ax=axes[1])
# plt.savefig('../../output/figs/cq-' + const_name + '-test.png', format='png', dpi=300)

# Plot the data of different small time periods
time_period = ['2019-12-01', '2020-02-01']
cq_sliced = cq.loc[time_period[0]:time_period[1], :]


cq_line_plot(cq_sliced, ylabel_str, logy=True)

plt.savefig('../../output/figs/cq-' + const_name + 'mobilization-period2.png', format='png', dpi=300)



