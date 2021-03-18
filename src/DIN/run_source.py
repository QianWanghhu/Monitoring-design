import veneer
from veneer.pest_runtime import *
from veneer.manage import start,kill_all_now
import pandas as pd
import time
import os
import spotpy as sp


output_file = 'output.txt'
veneer_port = find_port() 
vs = veneer.Veneer(port=veneer_port)

parameters = pd.read_csv('parameters.csv')
print('Read Parameters')
import pdb; pdb.set_trace()
parameter_dict = {}
for i,j in parameters.iterrows():
    scaled_value = (j.upper - j.lower) * j.value/100 + j.lower 
    parameter_dict[j.parameter] = scaled_value
    
    
NODEs = ['126001A']
things_to_record = [{'NetworkElement':node,'RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'} for node in NODEs]
vs.configure_recording(disable=[{}], enable=things_to_record)

vs.model.catchment.generation.set_param_values('DeliveryRatioSurface', parameter_dict['DRF'],  fus=['Sugarcane'])
vs.model.catchment.generation.set_param_values('DeliveryRatioSeepage', parameter_dict['DRP'],  fus=['Sugarcane'])
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

start_date = '01/07/2008'; end_date='01/07/2016'
vs.drop_all_runs()
vs.run_model(params={'NoHardCopyResults':True}, start = start_date, end = end_date) 


column_names = ['Load']
criteria = {'NetworkElement':'126001A','RecordingVariable':'Constituents@N_DIN@Downstream Flow Mass'}
get_din = vs.retrieve_multiple_time_series(criteria=criteria)

get_din.columns = column_names

din = get_din.loc[pd.Timestamp('2010-07-01'):pd.Timestamp('2016-06-30')]

with open(output_file, 'w') as f:
    f.write('---- CONSTITUENT LOADS ----  \n')

    f.write('---- DIN LOADS ----  \n')
    for i, j in din.iterrows():
        f.write(str(j[0]) + '\n')     


