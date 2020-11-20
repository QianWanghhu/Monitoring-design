# RUN SOURCE to generate observation_ensemble.csv
import pandas as pd
import veneer
from veneer.pest_runtime import *
from veneer.manage import start,kill_all_now
import time
import os
import spotpy as sp

first_port=15000
num_copies = 1
# define catchment_project and veneer_exe
project_path = './pest_source/'
catchment_project= project_path + '/MW_BASE_RC10.rsproj'

# Setup Veneer
# define paths to veneer command and the catchment project
veneer_path = project_path + '/vcmd45/FlowMatters.Source.VeneerCmd.exe'
#Now, go ahead and start source
processes,ports = start(catchment_project,
                        n_instances=num_copies,
                        ports=first_port,
                        debug=True,
                        veneer_exe=veneer_path,
                        remote=False,
                        overwrite_plugins=True)

veneer_port = first_port 
vs = veneer.Veneer(port=veneer_port)

parameters = pd.read_csv('parameter_ensemble.csv')
    
NODEs = ['126001A']
things_to_record = [{'NetworkElement':node,'RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'} for node in NODEs]
vs.configure_recording(disable=[{}], enable=things_to_record)

parameter_dict = parameters.iloc[0]

vs.model.catchment.generation.set_param_values('DeliveryRatioSurface',parameter_dict['DRF'],  fus=['Sugarcane'])
vs.model.catchment.generation.set_param_values('DeliveryRatioSeepage',parameter_dict['DRP'],  fus=['Sugarcane'])
vs.model.catchment.generation.set_param_values('DWC', parameter_dict['DWC'], fus=['Sugarcane'])
vs.model.catchment.generation.set_param_values('Load Conversion Factor', parameter_dict['LCF'], fus=['Sugarcane'])
vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['cDWC'], fus=['Cropping'])
vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['cEMC'], fus=['Cropping'])
vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['gDWC'], fus=['Grazing Open', 'Grazing Open'])
vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['gEMC'], fus=['Grazing Open', 'Grazing Open'])
vs.model.catchment.generation.set_param_values('dissConst_DWC', parameter_dict['oDWC'], fus=['Conservation', 'Forestry', 'Horticulture', 'Urban', 'Other'])
vs.model.catchment.generation.set_param_values('dissConst_EMC', parameter_dict['oEMC'], fus=['Conservation', 'Forestry', 'Horticulture', 'Urban', 'Other'])


vs.drop_all_runs()
vs.run_model(params={'NoHardCopyResults':True}) 


column_names = ['Load']
criteria = {'NetworkElement':'126001A','RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'}
get_din = vs.retrieve_multiple_time_series(criteria=criteria)

get_din.columns = column_names

observed_data = pd.read_csv('126001A_observations.csv')

din = get_din.loc[pd.Timestamp('2006-07-01'):pd.Timestamp('2018-06-30')]

pbias_din = 1 - sp.objectivefunctions.pbias(observed_data['DIN'], din['Load'])


with open(output_file, 'w') as f:
    f.write('---- DIN PBIAS ----  \n')
    f.write(str(pbias_din) + '\n')

    f.write('---- CONSTITUENT LOADS ----  \n')

    f.write('---- DIN LOADS ----  \n')
    for i, j in din.iterrows():
        f.write(str(j[0]) + '\n')

        
        


