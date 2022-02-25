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
FOLDER_EV = '/media/DataStager2/ERA5_EV/'

print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Open the files
# =============================================================================

# open the dataset
dD3 = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_DE_2030.nc').DEM
dD4 = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_DE_2040.nc').DEM
dG3 = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_GA_2030.nc').DEM
dG4 = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_GA_2040.nc').DEM
dN2 = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_NT_2025.nc').DEM
dN3 = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_NT_2030.nc').DEM
dN4 = xr.open_dataset(FOLDER_STORE+'ERA5_LoadModelData_NT_2040.nc').DEM

dG4m = dG4.mean()
dG3m = dG3.mean()
dD3m = dD3.mean()
dD4m = dD4.mean()

# =============================================================================
# fix the information when one set per scenario is missing
# =============================================================================

#TR00 in GA_2030
TMP=dG4.sel(region='TR00')/dG4m*dG3.mean()
dG3 = xr.where(dG3.region == 'TR00', TMP, dG3)

#AL00 in DE_2040
TMP=dD3.sel(region='AL00')/dD3m*dD4m
dD4 = xr.where(dD4.region == 'AL00', TMP, dD4)


#CH00 in GA_2030
TMP=dG4.sel(region='CH00')/dG4m*dG3.mean()
dG3 = xr.where(dG3.region == 'CH00', TMP, dG3)

#CH00 in DE_2040
TMP=dD3.sel(region='CH00')/dD3m*dD4m
dD4 = xr.where(dD4.region == 'CH00', TMP, dD4)


#FR15 in DE_2040
TMP=dD3.sel(region='FR15')/dD3m*dD4m
dD4 = xr.where(dD4.region == 'FR15', TMP, dD4)

#PL00 in DE_2040
TMP=dD3.sel(region='PL00')/dD3m*dD4m
dD4 = xr.where(dD4.region == 'PL00', TMP, dD4)

# =============================================================================
# Fix the information for double missing
# =============================================================================

#AL00 in GA_2030
TMP=dD3.sel(region='AL00')  / dD3m *dG3m
dG3 = xr.where(dG3.region == 'AL00', TMP, dG3)

#AL00 in GA_2040
TMP=dD4.sel(region='AL00')  / dD4m * dG4m
dG4 = xr.where(dG4.region == 'AL00', TMP, dG4)

#FR00 in GA_2030
TMP=dD3.sel(region='FR00')  / dD3m *dG3m
dG3 = xr.where(dG3.region == 'FR00', TMP, dG3)

#FR00 in GA_2040
TMP=dD4.sel(region='FR00')  / dD4m * dG4m
dG4 = xr.where(dG4.region == 'FR00', TMP, dG4)

#FR00 in GA_2030
TMP=dD3.sel(region='FR15')  / dD3m *dG3m
dG3 = xr.where(dG3.region == 'FR15', TMP, dG3)

#FR00 in GA_2040
TMP=dD4.sel(region='FR15')  / dD4m * dG4m
dG4 = xr.where(dG4.region == 'FR15', TMP, dG4)

#PL00 in GA_2030
TMP=dD3.sel(region='PL00')  / dD3m *dG3m
dG3 = xr.where(dG3.region == 'PL00', TMP, dG3)

#PL00 in GA_2040
TMP=dD4.sel(region='PL00')  / dD4m * dG4m
dG4 = xr.where(dG4.region == 'PL00', TMP, dG4)

#TR00 in DE_2030
TMP=dG3.sel(region='TR00')  /dG3m * dD3m
dD3 = xr.where(dD3.region == 'TR00', TMP, dD3)

#TR00 in DE_2040
TMP=dG4.sel(region='TR00')  / dG4m * dD4m
dD4 = xr.where(dD4.region == 'TR00', TMP, dD4)


# =============================================================================
# And then there is ukrain
# =============================================================================
#UA01 in GA_2030
TMP=dN3.sel(region='UA01')  / dN3.mean() *dG3m
dG3 = xr.where(dG3.region == 'UA01', TMP, dG3)

#UA01 in GA_2040
TMP=dN4.sel(region='UA01')  / dN4.mean() * dG4m
dG4 = xr.where(dG4.region == 'UA01', TMP, dG4)

#UA01 in DE_2030
TMP=dN3.sel(region='UA01')  /dN3.mean() * dD3m
dD3 = xr.where(dD3.region == 'UA01', TMP, dD3)

#UA01 in DE_2040
TMP=dN4.sel(region='UA01')  / dN4.mean() * dD4m
dD4 = xr.where(dD4.region == 'UA01', TMP, dD4)


#%%
# =============================================================================
# Cleaning time
# =============================================================================
dD3 = dD3.dropna(dim='region')
dD4 = dD4.dropna(dim='region')
dG3 = dG3.dropna(dim='region')
dG4 = dG4.dropna(dim='region')
dN2 = dN2.dropna(dim='region')
dN3 = dN3.dropna(dim='region')
dN4 = dN4.dropna(dim='region')



#%%
# =============================================================================
# Data saving
# =============================================================================
# Saving the file
dD3.to_netcdf(FOLDER_EV+'ERA5_EV_DEM_DE_2030.nc', encoding={'time':{'units':'days since 1900-01-01'}})
dD4.to_netcdf(FOLDER_EV+'ERA5_EV_DEM_DE_2040.nc', encoding={'time':{'units':'days since 1900-01-01'}})
dG3.to_netcdf(FOLDER_EV+'ERA5_EV_DEM_GA_2030.nc', encoding={'time':{'units':'days since 1900-01-01'}})
dG4.to_netcdf(FOLDER_EV+'ERA5_EV_DEM_GA_2040.nc', encoding={'time':{'units':'days since 1900-01-01'}})
dN2.to_netcdf(FOLDER_EV+'ERA5_EV_DEM_NT_2025.nc', encoding={'time':{'units':'days since 1900-01-01'}})
dN3.to_netcdf(FOLDER_EV+'ERA5_EV_DEM_NT_2030.nc', encoding={'time':{'units':'days since 1900-01-01'}})
dN4.to_netcdf(FOLDER_EV+'ERA5_EV_DEM_NT_2040.nc', encoding={'time':{'units':'days since 1900-01-01'}})

dD3.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_DEM_DE_2030.csv')
dD4.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_DEM_DE_2040.csv')
dG3.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_DEM_GA_2030.csv')
dG4.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_DEM_GA_2040.csv')
dN2.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_DEM_NT_2025.csv')
dN3.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_DEM_NT_2030.csv')
dN4.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_DEM_NT_2040.csv')
      
