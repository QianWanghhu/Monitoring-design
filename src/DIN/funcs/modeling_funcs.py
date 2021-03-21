# RUN SOURCE to generate observation_ensemble.csv
import pandas as pd
import numpy as np
import veneer
from veneer.pest_runtime import *
from veneer.manage import start,kill_all_now
import time
import os
import spotpy as sp
# Import packages
import SALib
from SALib.sample import latin

def generate_observatio_noised(vs, criteria, start_date, end_date):
    # install the results into a csv
    load = pd.DataFrame()
    print('Run the model to produce synthetic observations')

    time_start = time.time()
    vs.drop_all_runs()
    vs.run_model(params={'NoHardCopyResults':True}, start = start_date, end = end_date) 
    
    column_names = ['DIN_obs_load']
    get_din = vs.retrieve_multiple_time_series(criteria=criteria)
    get_din.columns = column_names
    din = get_din.loc[pd.Timestamp('2010-07-01'):pd.Timestamp('2016-06-30')]
    # store the daily results and the index of sampling
    load = pd.concat([load, din], axis=1)
    time_end = time.time()
    print(f'{time_end - time_start} seconds')
    load.to_csv('src/data/observation.csv')
    vs.drop_all_runs()
    print('----------Finished-----------')


def generate_observation_ensemble(vs_list, criteria, start_date, end_date):
    num_copies = len(vs_list)     
    # install the results into a csv
    load = pd.DataFrame()
    time_start = time.time()
    parameters = pd.read_csv('src/DIN/parameter_ensemble.csv', index_col='real_name') #OED/src/DIN/
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
            vs = change_param_values(vs, parameter_dict)
            response = vs.run_model(params={'NoHardCopyResults':True}, start=start_date, end=end_date, run_async=True)
            group_run_responses.append(response)

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

    # set the parameter to initial values
    for vs in vs_list:
        initial_values = obtain_initials(vs)
        vs = change_param_values(vs, initial_values)

    # kill_all_now()
    time_end = time.time()
    print(f'{time_end - time_start} seconds')

    load.to_csv('src/data/din_daily.csv')

def generate_parameter_ensemble(nsample, param_ensemble, datapath, seed=None):
    """
    The function is used to generate the parameter and data ensemble.
    The parameters are generated with Sobol' sampling or LHS.
    Parameters:
    ===========
    nsample: int, the number of parameter samples to generate (e.g., 512)
    param_ensemble: the name containing the relative path of parameter ensemble
    seed: int, the random seed to generate samples, default is None

    Returns:
    ===========
    None. Save parameter results to the given path.
    """
    fname = param_ensemble
    if not os.path.exists(fname):      
        parameters = pd.read_csv(datapath + 'Parameters.csv', index_col = 'Index')

        problem = {
            'num_vars': parameters.shape[0],
            'names': parameters.Name_short.values,
            'bounds': parameters.loc[:, ['Min', 'Max']].values
            }
        parameters_ensemble = latin.sample(problem, nsample, seed=88)
        df = pd.DataFrame(data=parameters_ensemble, index = np.arange(nsample), columns=problem['names'])
        df.index.name = 'real_name'
        df.to_csv(param_ensemble)
    else:
        print(f'The file of parameter ensemble exists under the folder')

def change_param_values(v, pvalue_dict):
    v.model.catchment.generation.set_param_values('DeliveryRatioSurface',pvalue_dict['DRF'],  fus=['Sugarcane'])
    v.model.catchment.generation.set_param_values('DeliveryRatioSeepage',pvalue_dict['DRP'],  fus=['Sugarcane'])
    v.model.catchment.generation.set_param_values('DWC', pvalue_dict['DWC'], fus=['Sugarcane'])
    v.model.catchment.generation.set_param_values('Load_Conversion_Factor', pvalue_dict['LCF'], fus=['Sugarcane'])
    v.model.catchment.generation.set_param_values('dissConst_DWC', pvalue_dict['gfDWC'], fus=['Grazing Forested'])
    v.model.catchment.generation.set_param_values('dissConst_EMC', pvalue_dict['gfEMC'], fus=['Grazing Forested'])
    v.model.catchment.generation.set_param_values('dissConst_DWC', pvalue_dict['goDWC'], fus=['Grazing Open'])
    v.model.catchment.generation.set_param_values('dissConst_EMC', pvalue_dict['goEMC'], fus=['Grazing Open'])
    v.model.catchment.generation.set_param_values('dissConst_DWC', pvalue_dict['cDWC'], fus=['Conservation'])
    v.model.catchment.generation.set_param_values('dissConst_EMC', pvalue_dict['cEMC'], fus=['Conservation'])
    v.model.catchment.generation.set_param_values('dissConst_DWC', pvalue_dict['fDWC'], fus=['Forestry'])
    v.model.catchment.generation.set_param_values('dissConst_EMC', pvalue_dict['fEMC'], fus=['Forestry'])
    v.model.catchment.generation.set_param_values('dissConst_DWC', pvalue_dict['oDWC'], fus=['Horticulture', 'Urban', 'Water', 'Other', 'Irrigated Cropping'])
    v.model.catchment.generation.set_param_values('dissConst_EMC', pvalue_dict['oEMC'], fus=['Horticulture', 'Urban', 'Water', 'Other', 'Irrigated Cropping'])
    return v

# obtain initial values
def obtain_initials(v):
    """Obtain the initial values of the model.
    Parameters:
    ===========
    v: veneer objects.

    Returns:
    ========
    initial_values: dict, initla values of parameters
    """
    initial_values = {}
    initial_values['DRF'] = v.model.catchment.generation.get_param_values('DeliveryRatioSurface', fus=['Sugarcane'])
    initial_values['DRP'] = v.model.catchment.generation.get_param_values('DeliveryRatioSeepage',  fus=['Sugarcane'])
    initial_values['DWC'] = v.model.catchment.generation.get_param_values('DWC', fus=['Sugarcane'])
    initial_values['LCF'] = v.model.catchment.generation.get_param_values('Load_Conversion_Factor', fus=['Sugarcane'])
    initial_values['gfDWC'] = v.model.catchment.generation.get_param_values('dissConst_DWC', fus=['Grazing Forested'])
    initial_values['gfEMC'] = v.model.catchment.generation.get_param_values('dissConst_EMC', fus=['Grazing Forested'])
    initial_values['goDWC'] = v.model.catchment.generation.get_param_values('dissConst_DWC', fus=['Grazing Open'])
    initial_values['goEMC'] = v.model.catchment.generation.get_param_values('dissConst_EMC', fus=['Grazing Open'])
    initial_values['cDWC'] = v.model.catchment.generation.get_param_values('dissConst_DWC', fus=['Conservation'])
    initial_values['cEMC'] = v.model.catchment.generation.get_param_values('dissConst_EMC', fus=['Conservation'])
    initial_values['fDWC'] = v.model.catchment.generation.get_param_values('dissConst_DWC', fus=['Forestry'])
    initial_values['fEMC'] = v.model.catchment.generation.get_param_values('dissConst_EMC', fus=['Forestry'])
    initial_values['oDWC'] = v.model.catchment.generation.get_param_values('dissConst_DWC', fus=['Horticulture', 'Urban', 'Water', 'Other', 'Irrigated Cropping'])
    initial_values['oEMC'] = v.model.catchment.generation.get_param_values('dissConst_EMC', fus=['Horticulture', 'Urban', 'Water', 'Other', 'Irrigated Cropping'])
    
    return initial_values

def modeling_settings():
    NODEs = ['126001A']
    things_to_record = [{'NetworkElement':node,'RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'} for node in NODEs]
    criteria = {'NetworkElement':'126001A','RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'}
    start_date = '01/07/2008'; end_date='01/07/2016'
    return NODEs, things_to_record, criteria, start_date, end_date


def vs_settings(ports, things_to_record):
    """
    Set up the vs objects.
    Parameters:
    ===========
    ports: list, list of ports to generate veneer objects
    things_to_record: dict, configurations of vs objects

    Returns:
    ===========
    vs_list: list, list of vs ojeects

    """
    vs_list = []
    for veneer_port in ports:
        # veneer_port = first_port 
        vs_list.append(veneer.Veneer(port=veneer_port))
    
    for vs in vs_list:
        vs.configure_recording(disable=[{}], enable=things_to_record)
    return vs_list
