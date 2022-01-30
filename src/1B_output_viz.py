#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 09:34:10 2022

@author: Laurens Stoop - l.p.stoop@uu.nl
"""
#%%
# =============================================================================
# Dependencies
# =============================================================================


## Importing modules
import xarray as xr 
import numpy as np
import regionmask
import geopandas as gpd
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os.path


# Location of datasets
FOLDER_EV = '/media/DataStager2/ERA5_CF_MZ/'
FOLDER_PECD = '/media/DataStager1/Other/PECDv3.1/'


year = '2010'
zone = 'NL00'
variable = 'SolarPV'

#%%
# =============================================================================
# Loading the EV & PECD data
# =============================================================================

# EV versions 
dsR = xr.open_dataset(FOLDER_EV+'ERA5_CF_MZ_RM_'+year+'.nc')
dsW = xr.open_dataset(FOLDER_EV+'ERA5_CF_MZ_WM_'+year+'.nc')

# Clean the leap-days out of the data
dsR = dsR.sel(time=~((dsR.time.dt.month == 2) & (dsR.time.dt.day == 29)))
dsW = dsW.sel(time=~((dsW.time.dt.month == 2) & (dsW.time.dt.day == 29)))


# Load the PECD
dfP = pd.read_csv(FOLDER_PECD+'PECD_'+variable+'_2030_edition 2021.3_'+zone+'.csv', sep=',', skiprows=10, header=[0]) #, names=['Code', 'Type', 'Capacity'])

# # Stack the PECD data columsn 
# part1 = df.iloc[:,0:2]
# part2 = df.iloc[:,2:4]

# new_columns = ["c", "d"]
# part1.columns = new_columns
# part2.columns = new_columns

# print pd.concat([part1, part2], ignore_index=True)

#%%
# =============================================================================
# make some figures
# =============================================================================
plt.figure(figsize=(8,8))
ax = plt.axes()
plt.scatter(dfP['2010'], dsW.SPV.sel(region=zone, time=dsW.time.dt.year == 2010), alpha = 0.2, facecolors='b', s=1, label="CF-Weighted")
plt.scatter(dfP['2010'], dsR.SPV.sel(region=zone, time=dsR.time.dt.year == 2010), alpha = 0.2, facecolors='g', s=1, label="Regular")
plt.legend(loc="upper left", markerscale=8)
plt.xlabel('PECDV3.1 data')
plt.ylabel('ERA5 data')
plt.title(zone+' '+variable)
plt.ylim(0, 1)
plt.xlim(0, 1)



#%%
# =============================================================================
# Bias adjustment
# =============================================================================
dfP.drop(['Date', 'Hour'], axis=1).mean().mean()
