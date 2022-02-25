#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remade on 25 feb 2022

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

import matplotlib.pyplot as plt


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
    'ITS1','ITSA','ITSI','LT00',
    'LU00',
    'LV00','ME00','MK00','MT00','NL00',
    'NOM1','NON1','NOS0','PL00','PT00',
    'RO00','RS00','SE01','SE02','SE03',
    'SE04','SI00','SK00','TR00','UA01',
    'UK00','UKNI']



region_names_fix = ['ITSI', 'LB00', 'PL00', 'LT00', 'LU00', 'BG00', 'NON1', 'CZ00', 'SK00',
       'CH00', 'SY00', 'FR15', 'RS00', 'NOS0', 'IE00', 'DE00', 'AT00', 'MD00',
       'ES00', 'AL00', 'RO00', 'ME00', 'HR00', 'DKE1', 'LV00', 'NL00', 'TR00',
       'MA00', 'EL00', 'EL03', 'TN00', 'EG00', 'UA01', 'UA02', 'BE00', 'MK00', # change GR to EL
       'ITN1', 'PT00', 'DKW1', 'UK00', 'BA00', 'SI00', 'DZ00', 'IL00', 'CY00',
       'UKNI', 'NOM1', 'FI00', 'LY00', 'EE00', 'SE01', 'FR00', 'SE02', 'SE03',
       'SE04', 'HU00', 'ITSA', 'ITCA', 'ITCN', 'ITCS', 'ITS1']

# Read NetCDF
FOLDER_STORE = '/media/DataStager2/ERA5_LoadModel/'

print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Open the files
# =============================================================================

scenario_capacity = 'DE_2030'
region_name = 'EL00'

   

    
# open data
dsd = xr.open_dataset(FOLDER_STORE+'ERA5_DEM_'+scenario_capacity+'.nc')
dst = xr.open_mfdataset(FOLDER_STORE+'ERA5_PWT_*.nc' )

# make sure to only use similair time period
dst = dst.sel(time=slice('1982-01-01', '2016-12-31'))
dst = dst.sel(time=~((dst.time.dt.month == 2) & (dst.time.dt.day == 29)))
dst['region'] = region_names_fix

        
# create one dataset
ds = xr.Dataset()
ds['PWT'] = dst.PWT
ds['DEM'] = dsd.DEM

# some regions are not listed
ds.fillna(0)
ds = ds.sel(time=slice('2010-01-01', '2016-12-31'),drop=True)

plt.close('all')
fig = plt.figure()
plt.scatter(dst.PWT.sel(region=region_name),dsd.DEM.sel(region=region_name), s=0.3)
plt.xlabel('Population weighted temperature [degC]')
plt.ylabel('Estimated load [MW]')
plt.title('Time slice 2010-2016')
plt.tight_layout()
# plt.ioff()
# plt.savefig('/home/stoop/Documents/Project/EnergyVariables-EV/results/figures/DemandPWT/DemPwT_'+scenario_capacity+'_'+region_name+'.png')
        
#%%
# =============================================================================
# Filtered view
# =============================================================================


ds1 = ds.where(ds['time.dayofweek'] == 0, drop=True)
ds2 = ds.where(ds['time.dayofweek'] == 1, drop=True)
ds3 = ds.where(ds['time.dayofweek'] == 2, drop=True)
ds4 = ds.where(ds['time.dayofweek'] == 3, drop=True)
ds5 = ds.where(ds['time.dayofweek'] == 4, drop=True)
ds6 = ds.where(ds['time.dayofweek'] == 5, drop=True)
ds7 = ds.where(ds['time.dayofweek'] == 6, drop=True)

fig = plt.figure()
plt.scatter(ds1.PWT.sel(region=region_name),ds1.DEM.sel(region=region_name), s=0.1)
plt.scatter(ds2.PWT.sel(region=region_name),ds2.DEM.sel(region=region_name), s=0.1)
plt.scatter(ds3.PWT.sel(region=region_name),ds3.DEM.sel(region=region_name), s=0.1)
plt.scatter(ds4.PWT.sel(region=region_name),ds4.DEM.sel(region=region_name), s=0.1)
plt.scatter(ds5.PWT.sel(region=region_name),ds5.DEM.sel(region=region_name), s=0.1)
plt.scatter(ds6.PWT.sel(region=region_name),ds6.DEM.sel(region=region_name), s=0.1)
plt.scatter(ds7.PWT.sel(region=region_name),ds7.DEM.sel(region=region_name), s=0.1)
plt.xlabel('Population weighted temperature [degC]')
plt.ylabel('Estimated load [MW]')
plt.title('Time slice 2010-2016')
plt.tight_layout()
# plt.ioff()
# plt.savefig('/home/stoop/Documents/Project/EnergyVariables-EV/results/figures/DemandPWT/DemPwT_'+scenario_capacity+'_'+region_name+'_dow.png')
