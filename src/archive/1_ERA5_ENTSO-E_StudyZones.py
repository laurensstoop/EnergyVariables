#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restructered on Thu 19 May 2021 21:40

@author: Laurens Stoop - l.p.stoop@uu.nl

Following example by Matteo de Felice: http://www.matteodefelice.name/post/aggregating-gridded-data/
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
# import pandas as pd
import matplotlib.pyplot as plt

# Set the path for the data

PATH_TO_NUTS0 = '/media/DataDrive/Other/RegionDefinitions/ENTSO-E_StudyZones/DTU-PECD22-Polygons_SZ_VF2021.shp'
PATH_TO_NUTS1 = '/media/DataDrive/Other/RegionDefinitions/ENTSO-E_StudyZones/DTU-PECD22-Polygons_VF2021.shp'

# Read NetCDF
FOLDER_WITH_NETCDF = '/media/DataGate3/ERA5-EU_CF/'


print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Load in the base shapefile 
# =============================================================================

# Load the shapefile
nuts0 = gpd.read_file(PATH_TO_NUTS0)
nuts1 = gpd.read_file(PATH_TO_NUTS1)

# There is an abandoned LY00 zone in there 
# nuts1.iloc[246]
nuts1 = nuts1.drop(index=246)

# To check some info you could read the headers of the shapefiles
# nuts0.head() # to check the contents      --> 121 on-/offshore definitions
# nuts1.head() # to check the contents      --> 262 on-/offshore definitions


#%%
# =============================================================================
# Load in the datafiles them self
# =============================================================================

# Load in the NetCDF
ds = xr.open_mfdataset(FOLDER_WITH_NETCDF+'ERA5-EU_CF_2011.nc') #, chunks = {'time': 8760})

#%%
# =============================================================================
# Now we define the regionmask and apply it
# =============================================================================

# CALCULATE MASK
# SZ0_mask_poly = regionmask.Regions(name = 'ENTSO-E_StudyZone0_Mask', numbers = list(range(0,121)), abbrevs = list(nuts0['Study Zone']), outlines = list(nuts0.geometry.values[i] for i in range(0,121))) # names = list(nuts0['Study Zone']),
SZ1_mask_poly = regionmask.Regions(name = 'ENTSO-E_StudyZone1_Mask', numbers = list(range(0,262)), abbrevs = list(nuts1['Code']), outlines = list(nuts1.geometry.values[i] for i in range(0,262))) # names = list(nuts1['Study Zone']),
# print(nuts_mask_poly)

# Create the mask
mask = SZ1_mask_poly.mask(ds.isel(time = 0), method = None)
# mask # To check the contents of the mask defined

# =============================================================================
# A quick figure for sanity checks
# =============================================================================
plt.figure(figsize=(12,8))
ax = plt.axes()
mask.plot(ax = ax)
nuts1.plot(ax = ax, alpha = 0.8, facecolor = 'none', lw = 1)





#%%
# =============================================================================
# Now selecting a region to select the data
# =============================================================================

# Select a region (the Netherlands is 38/148)
ID_REGION = 150

# Select the lat/lon combo's as vector to use later
lat = mask.lat.values
lon = mask.lon.values

# We select the region under consideration
sel_mask = mask.where(mask == ID_REGION).values

# Select the specific lat/lon combo that is the minimum bounding box
id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

# This is the fancy loop by Matteo that uses the compute dask function to load and slice the data
out_sel = ds.sel(lat = slice(id_lat[0], id_lat[-1]), lon = slice(id_lon[0], id_lon[-1])).compute().where(mask == ID_REGION)

# =============================================================================
# A quick figure for the sanity checks
# =============================================================================
plt.figure(figsize=(12,8))
ax = plt.axes()
out_sel.solarCF.isel(time = 4140).plot(ax = ax)
nuts1.plot(ax = ax, alpha = 0.8, facecolor = 'none')



#%%
# =============================================================================
# Regional mean for saving data
# =============================================================================

# Now calculate the regional mean 
x = out_sel.solarCF.groupby('time').mean(...)
x.plot()

# # Saving function
# x.t2m.to_pandas().to_csv('average-temperature.csv', header = ['t2m'])
