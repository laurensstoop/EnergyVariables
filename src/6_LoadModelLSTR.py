#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Made on 28 feb 2022

@author: Laurens Stoop - l.p.stoop@uu.nl

"""

#%%
# =============================================================================
# Dependencies
# =============================================================================


## Importing modules
import xarray as xr 
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import least_squares as lsq
from scipy.optimize import curve_fit
from scipy import stats

#import local package
# import rtts

# Versions of the 
TYNDP_scenarios_capacity = np.array([
            'DE_2030', 
            'DE_2040',
            'GA_2030', 
            'GA_2040', 
            'NT_2025', 
            'NT_2030', 
            'NT_2040'
        ])


region_names = [
    'AL00','AT00','BA00','BE00','BG00',
    'CH00','CY00','CZ00','DE00','DKE1',
    'DKKF','DKW1','EE00','EL00','EL03',
    'ES00','FI00','FR00','FR15','HR00',
    'HU00','IE00','ITCN','ITCS','ITN1',
    'ITS1','ITSA','ITSI','LT00','LU00',
    'LV00','ME00','MK00','MT00','NL00',
    'NOM1','NON1','NOS0','PL00','PT00',
    'RO00','RS00','SE01','SE02','SE03',
    'SE04','SI00','SK00','TR00','UA01',
    'UK00','UKNI']


# Read NetCDF
FOLDER_STORE = '/media/DataStager2/ERA5_LoadModel/'

print('NOTIFY: Initialization is complete, Skynet active')
#%%



scenario_capacity = 'DE_2030'
region_name = 'FR00'


#%%
# =============================================================================
# Open the files
# =============================================================================

# open the dataset
ds = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_'+scenario_capacity+'.nc')

# prep the data to a single region
dsr = xr.Dataset()
dsr = ds.sel(region=region_name)
# Convert to a dataframe
df = dsr.to_dataframe()

#%%
# =============================================================================
# Splitting the data
# =============================================================================

# x_train, x_test, y_train, y_test = rtts.region_train_test_split(df.drop(columns=['DEM']), df.DEM)


#%%
# =============================================================================
# Fitting the data
# =============================================================================

# Function definition
def LSTRmodel(temp, C):
    G = 1/(1 + np.exp( -C[4]*(temp - C[5])))
    return (C[0] + C[1]*temp)*(1 - G) + (C[2] + C[3]*temp)*G


# Function definition
def LSTRmodelResidual(C,temp, dem):
    return LSTRmodel(temp, C) - dem

# Initial guess of the fit
x0 = [
      75000.,    # Zero crossing left branch
      -3200., # slope left branch
      8000.,    # Zero crossing right branch
      1000.,  # slope right branch
      1.,    # Gamma factor (unkown, guess = 1)
      15.0  # Inflection point from literature (J. Moral-Carcedo, J. Vicens-Otero / Energy Economics 27 (2005) 477–494)
      ]

# The fitting procedure
fitvalues = lsq(LSTRmodelResidual, x0, loss='soft_l1', f_scale=0.00001, args=(dsr.PWT, dsr.DEM))



# perr = np.sqrt(np.diag(fitvalues.jac))

# =============================================================================
# Check if data is good
# =============================================================================

# temp_test = np.linspace(dsr.PWT.min().values, dsr.PWT.max().values, 300)
# demand_test = LSTRmodel(temp_test, fitvalues.x)

# The data moddeled to which the fit is made
dsr['lstrDEM'] = LSTRmodel(dsr.PWT, fitvalues.x)

# The r value
r = stats.linregress(dsr.DEM,dsr.lstrDEM)

# The RMSE value
rmse = np.sqrt(((dsr.DEM - dsr.lstrDEM) ** 2).mean())

fig = plt.figure()
plt.scatter(dsr.DEM, dsr.lstrDEM, s=0.3)
plt.title('R '+str(r.rvalue))

