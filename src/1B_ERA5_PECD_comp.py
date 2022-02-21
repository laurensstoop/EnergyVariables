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
FOLDER_EV = '/media/DataStager2/ERA5_EV/'
FOLDER_PECD = '/media/DataStager1/Other/PECDv3.1/'


#%%
# =============================================================================
# Loading the EV & PECD data
# =============================================================================

# EV versions 
dsR = xr.open_dataset(FOLDER_EV+'ERA5_EV_RM_2010.nc')
dsW = xr.open_dataset(FOLDER_EV+'ERA5_EV_WM_2010.nc')

# Load the PECD
df_TR = pd.read_csv(FOLDER_PECD+'PECD_Onshore_2030_edition 2021.3_TR00.csv', sep=',', skiprows=10, header=[0]) #, names=['Code', 'Type', 'Capacity'])
