# RUN SOURCE to generate observation_ensemble.csv
import pandas as pd
import numpy as np
import veneer
from veneer.pest_runtime import *
from veneer.manage import start,kill_all_now
import time
import os
import spotpy as sp

first_port=15000
num_copies = 1
# define catchment_project and veneer_exe
project_path = 'OED/src/DIN/pest_source/'
# project_path = 'pest_source/'
catchment_project= project_path + '/MW_BASE_RC10.rsproj'

# Setup Veneer
# define paths to veneer command and the catchment project
veneer_path = project_path + 'vcmd45/FlowMatters.Source.VeneerCmd.exe'
#Now, go ahead and start source
processes,ports = start(catchment_project,
                        n_instances=num_copies,
                        ports=first_port,
                        debug=True,
                        veneer_exe=veneer_path,
                        remote=False,
                        overwrite_plugins=True)

vs = veneer.Veneer(port=first_port)
    
NODEs = ['126001A']
things_to_record = [{'NetworkElement':node,'RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'} for node in NODEs]
vs.configure_recording(disable=[{}], enable=things_to_record)

# install the results into a csv
if not os.path.exists('observation.csv'):
    load = pd.DataFrame()

time_start = time.time()
start_date = '01/07/2008'; end_date='01/07/2016'
criteria = {'NetworkElement':'gauge_126001A_SandyCkHomebush','RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'}

vs.drop_all_runs()
vs.run_model(params={'NoHardCopyResults':True}, start = start_date, end = start_date) 
 
column_names = ['DIN_obs_load']
get_din = vs.retrieve_multiple_time_series(criteria=criteria)
get_din.columns = column_names
din = get_din.loc[pd.Timestamp('2010-07-01'):pd.Timestamp('2016-06-30')]
# store the daily results and the index of sampling
load = pd.concat([load, din], axis=1)

time_end = time.time()
print(f'{time_end - time_start} seconds')

# Add noise to the model outputs
from utils import generate_noise, noise_stats

noise_level = noise_stats(load.values, 0.1)
noise = generate_noise(load.shape[0], dist='normal', pars={'mean':0, 'std': noise_level})
load.loc[:, 'noised'] = load.loc[:, column_names] + noise 

load.to_csv('OED/data/observation.csv')
print('----------Finished-----------')