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
num_copies = 8
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
vs_list = []
for veneer_port in ports:
    # veneer_port = first_port 
    vs_list.append(veneer.Veneer(port=veneer_port))
    
NODEs = ['126001A']
things_to_record = [{'NetworkElement':node,'RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'} for node in NODEs]
for vs in vs_list:
    vs.configure_recording(disable=[{}], enable=things_to_record)

# install the results into a csv
if not os.path.exists('din_daily.csv'):
    load = pd.DataFrame()

time_start = time.time()
parameters = pd.read_csv('OED/src/DIN/parameter_ensemble.csv', index_col='real_name') #OED/src/DIN/
start_date = '01/07/2008'; end_date='01/07/2016'
criteria = {'NetworkElement':'gauge_126001A_SandyCkHomebush','RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'}
# parameters = parameters.iloc[0:12, :]

num_runs = parameters.shape[0]
group_loops = np.floor_divide(num_runs, num_copies) + 1
total_runs = 0
for index_group in range(group_loops):
    group_run_responses = []
    if index_group == (group_loops - 1):
        num_copies_loop = (num_runs - index_group * num_copies)
    else:
        num_copies_loop = num_copies
    for j in range(num_copies_loop):
        total_runs += 1
        if (index_group * num_copies + j) >= num_runs: break

        vs= vs_list[j]
        vs.drop_all_runs()

        parameter_dict = parameters.iloc[total_runs-1]
        # Make sure names of parameters are correct!
        vs.model.catchment.generation.set_param_values('DeliveryRatioSurface',parameter_dict['DRF'],  fus=['Sugarcane'])
        vs.model.catchment.generation.set_param_values('DeliveryRatioSeepage',parameter_dict['DRP'],  fus=['Sugarcane'])
        vs.model.catchment.generation.set_param_values('DWC', parameter_dict['DWC'], fus=['Sugarcane'])
        vs.model.catchment.generation.set_param_values('Load_Conversion_Factor', parameter_dict['LCF'], fus=['Sugarcane'])
        vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['gfDWC'], fus=['Grazing Forested'])
        vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['gfEMC'], fus=['Grazing Forested'])
        vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['goDWC'], fus=['Grazing Open'])
        vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['goEMC'], fus=['Grazing Open'])
        vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['cDWC'], fus=['Conservation'])
        vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['cEMC'], fus=['Conservation'])
        vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['fDWC'], fus=['Forestry'])
        vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['fEMC'], fus=['Forestry'])
        vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['oDWC'], fus=['Horticulture', 'Urban', 'Water', 'Other', 'Irrigated Cropping'])
        vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['oEMC'], fus=['Horticulture', 'Urban', 'Water', 'Other', 'Irrigated Cropping'])

        response = vs.run_model(params={'NoHardCopyResults':True}, start=start_date, end=end_date, run_async=True)
        group_run_responses.append(response)
        # vs.drop_all_runs()
        # vs.run_model(params={'NoHardCopyResults':True}, start='01/07/2004', end='01/07/2016') 
    for j in range(num_copies_loop):
        run_index = index_group * num_copies + j
        if (run_index) >= num_runs: break
            
        vs = vs_list[j]
        r = group_run_responses[j]   
        code = r.getresponse().getcode() # wait until the job finished   
        column_names = ['DIN_' + str(run_index)]
        get_din = vs.retrieve_multiple_time_series(criteria=criteria)
        get_din.columns = column_names
        din = get_din.loc[pd.Timestamp('2010-07-01'):pd.Timestamp('2016-06-30')]
        # store the daily results and the index of sampling
        load = pd.concat([load, din], axis=1)
    
    print(f'Finish {total_runs} runs')

time_end = time.time()
print(f'{time_end - time_start} seconds')

load.to_csv('OED/data/din_daily.csv')
