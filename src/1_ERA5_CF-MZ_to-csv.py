#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restructered on Sun 26 Jan 2022 17:04

@author: Laurens Stoop - l.p.stoop@uu.nl

Following example by Matteo de Felice: http://www.matteodefelice.name/post/aggregating-gridded-data/
"""

#%%
# =============================================================================
# Dependencies
# =============================================================================


## Importing modules
import xarray as xr 
import datetime
import numpy as np
import pandas as pd
import os.path


# Select the years to run
years = np.array([
            '1950', '1951', '1952',
            '1953', '1954', '1955',
            '1956', '1957', '1958',
            '1959', '1960', '1961',
            '1962', '1963', '1964',
            '1965', '1966', '1967',
            '1968', '1969', '1970',
            '1971', '1972', '1973',
            '1974', '1975', '1976',
            '1977', '1978',
            '1979', '1980', '1981',
            '1982', '1983', '1984',
            '1985', '1986', '1987',
            '1988', '1989', 
            '1990',
            '1991', '1992', '1993',
            '1994', '1995', '1996',
            '1997', '1998', '1999',
            '2000', '2001', '2002',
            '2003', '2004', '2005',
            '2006', '2007', '2008',
            '2009', '2010', '2011',
            '2012', '2013', '2014',
            '2015', '2016', '2017',
            '2018', '2019', 
            '2020'            
        ])

# Read NetCDF
FOLDER_WITH_NETCDF = '/media/DataStager2/ERA5_CF_MZ/'
FOLDER_STORE = '/media/DataStager2/ERA5_CF_MZ/csv/'




print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Load in the base shapefile 
# =============================================================================


#%%
# =============================================================================
# Load in the datafiles them self
# =============================================================================

# The mega loop
for year in years:
    # Define the file name
    file_save = FOLDER_STORE+'ERA5_CF_MZ_'+year+'.csv'
    
  
    
    # Check if file allready exist, then get out
    if os.path.isfile(file_save) == True:
        
        # Tell us the file exist
        print('NOTIFY: Allready applied for year '+year+'!')
      
        
    # IF the file doesn't exist, apply the distribution
    elif os.path.isfile(file_save) == False:
        
        print('NOTIFY: Working on year '+year+'!')
        
        # Load in the NetCDF
        ds = xr.open_mfdataset(FOLDER_WITH_NETCDF+'ERA5_CF_MZ_WM_'+year+'*.nc') 
        
        # make it a csv
        df_won = ds.WON.to_dataframe('region').unstack().T
        df_wof = ds.WOF.to_dataframe('region').unstack().T
        df_spv = ds.SPV.to_dataframe('region').unstack().T
        
        
        #%%                
        # =============================================================================
        # Setting units & saving
        # =============================================================================
        
        df_won.to_csv(FOLDER_STORE+'ERA5_CF-MZ_'+year+'_WON.csv') 
        df_wof.to_csv(FOLDER_STORE+'ERA5_CF-MZ_'+year+'_WOF.csv') 
        df_spv.to_csv(FOLDER_STORE+'ERA5_CF-MZ_'+year+'_SPV.csv') 