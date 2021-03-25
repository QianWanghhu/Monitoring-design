"""
Script used to run_source and return the output file.
"""
import veneer
from veneer.pest_runtime import *
from veneer.manage import start,kill_all_now
import pandas as pd
import time
import os
import spotpy as sp

from funcs.modeling_funcs import change_param_values, modeling_settings

output_file = 'output.txt'
veneer_port = find_port() 
vs = veneer.Veneer(port=veneer_port)

parameters = pd.read_csv('parameters.csv')
print('Read Parameters')
# import pdb; pdb.set_trace()
# Define objective functions
# Use average annual loads
def average_annual(data, year_length):
    """
    The average annual.
    """
    data_ave = data.sum()/year_length
    return data_ave
# End average_annual()

# Use annual or monthly loads
def timeseries_sum(df, temp_scale = 'Y'):
    """
    Obtain the sum of timeseries of different temporal scale.
    temp_scale: str, default is 'Y', monthly using 'M'
    """
    sum_126001A = df.resample(temp_scale).sum()
    return sum_126001A

# import observation if the output.txt requires the use of obs.
# Here the observation can be monitoring data or synthetic data.

parameter_dict = {}
for i,j in parameters.iterrows():
    scaled_value = (j.upper - j.lower) * j.value/100 + j.lower 
    parameter_dict[j.parameter] = scaled_value
    
# define the modeling period and the recording variables
NODEs, things_to_record, criteria, start_date, end_date = modeling_settings()
vs.configure_recording(disable=[{}], enable=things_to_record)

vs = change_param_values(vs, parameter_dict)
vs.drop_all_runs()
vs.run_model(params={'NoHardCopyResults':True}, start = start_date, end = end_date) 

# define the criteria for retrieve multiple_time_series
column_names = ['Load']
get_din = vs.retrieve_multiple_time_series(criteria=criteria)
get_din.columns = column_names
din = get_din.loc[pd.Timestamp('2010-07-01'):pd.Timestamp('2016-06-30')]

# obtain the sum at a given temporal scale
df = timeseries_sum(din, temp_scale = 'Y')

with open(output_file, 'w') as f:
    f.write('---- CONSTITUENT LOADS ----  \n')

    f.write('---- DIN LOADS ----  \n')
    for i, j in df.iterrows():
        f.write(str(j[0]) + '\n')     


