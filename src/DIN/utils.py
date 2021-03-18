# Import packages
import numpy as np
import pandas as pd


def generate_noise(size, dist = 'normal', pars={'mean': 0, 'std': 1}):
    """
    Help funtion to add noise to the model outputs.
    Parameters:
    -----------
    size : 
    dist : 
    pars : 

    Return:
    -------
    noise : 
    """
    if dist == 'normal':
        noise = np.random.normal(pars['mean'], pars['std'], size = size)
    else:
        raise Exception("Sorry, the type of distribution for noise is not included")

    return noise
# End add_noise()


def noise_stats(data, noise_level):
    """
    Help funtion to calculate the mean and standard deviation.
    Parameters
    -----------

    Return
    -------
    """
    if not isinstance(data, np.ndarray):
        raise Exception("data is not an array")

    if not isinstance(noise_level, float):
        raise Exception("noise_level is not an array")

    data_mean = data.mean()
    std_level = data_mean * noise_level

    return std_level

def pre_observation_pst(observation, obsnme, obgnme):
    """
    Format observartions into the .pst file for PEST++.
    Parameters:
    -----------

    Returns:
    ---------
    """ 
    obs_pst = pd.DataFrame(data = observation, columns = ['obsval'])
    obs_pst.index = obsnme
    obs_pst.loc[:, 'weight'] = 1 / obs_pst.shape[0]
    obs_pst.loc[:, 'obgnme'] = obgnme
    obs_pst.index.name = 'obsnme'

    return obs_pst

def generate_obsnme(x, obgnme):
    obsnme = pd.to_datetime(x).strftime("%d_%m_%Y")
    obsnme = [f'{obgnme}_{i}' for i in obsnme]  

    return obsnme
    
    


