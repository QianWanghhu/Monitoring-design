"""
RUN SOURCE to generate observation_ensemble.csv
"""
import pandas as pd
import numpy as np
import veneer
from veneer.pest_runtime import *
from veneer.manage import start,kill_all_now
import time
import os
import spotpy as sp

from funcs.modeling_funcs import change_param_values, obtain_initials, modeling_settings, vs_settings
from funcs.modeling_funcs import generate_observatio_noised, generate_observation_ensemble
from funcs.modeling_funcs import generate_parameter_ensemble

first_port=15000
num_copies = 8
# define catchment_project and veneer_exe
project_path = 'src/DIN/pest_source/'
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

NODEs, things_to_record, criteria, start_date, end_date = modeling_settings()
vs_list = vs_settings(ports, things_to_record)

# generate parameter emsenble
datapath = 'data/'
nsample = 512
param_ensemble = 'src/DIN/parameter_ensemble.csv'
generate_parameter_ensemble(nsample, param_ensemble, datapath, seed=88)

# check if there is a file containing synthetic observations
if not os.path.exists(f'{datapath}observation.csv'):
    generate_observatio_noised(vs_list[0], criteria, start_date, end_date)
else:
    print('observation.csv exists.')

# generate the observation ensemble
if not os.path.exists(f'{datapath}din_daily.csv'):
    generate_observation_ensemble(vs_list, criteria, start_date, end_date)
else:
    print('din_daily.csv exists.')

kill_all_now(processes)


