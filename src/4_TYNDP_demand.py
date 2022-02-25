#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remade on 21 feb 2022

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
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os.path



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
dem_file_loc='/media/DataStager1/Other/ElectricityDemand/TYNDP2020/'

print('NOTIFY: Initialization is complete, Skynet active')
#%%


for scenario_capacity in TYNDP_scenarios_capacity: 

    DEM=[]      
    REGION_NAME=[]   
    print(scenario_capacity)    
    
    for region_name in region_names:
        print('      : '+region_name+'!')
    #%%
    # =============================================================================
    # Select the relevant Demand data
    # =============================================================================
        
        dem=[]
        
       
        # Append all variables in the timespan    
        
        # Attempt for base cases
        try:
            df = pd.read_excel(dem_file_loc+'Demand_TimeSeries_'+scenario_capacity+'.xlsx', region_name, header=10)
            for year in np.arange(1982,2017):
                    dem.append(df[year].values)  
                    
        # In exceptional cases we try something else
        except ValueError:
            
            #First exception; luxembourg, add three regions
            if region_name == 'LU00':
                
                print('Luxembourg is special'+region_name)
                df1 = pd.read_excel(dem_file_loc+'Demand_TimeSeries_'+scenario_capacity+'.xlsx', 'LUB1', header=10)
                df2 = pd.read_excel(dem_file_loc+'Demand_TimeSeries_'+scenario_capacity+'.xlsx', 'LUF1', header=10)
                df3 = pd.read_excel(dem_file_loc+'Demand_TimeSeries_'+scenario_capacity+'.xlsx', 'LUG1', header=10)
                df = df1.fillna(0) + df2.fillna(0) + df3.fillna(0)
                for year in np.arange(1982,2017):
                    dem.append(df[year].values)  
                
            # For the Greece regions use correct naming
            elif region_name =='EL00': 
                print('Greece has incorrect region code ')
                df = pd.read_excel(dem_file_loc+'Demand_TimeSeries_'+scenario_capacity+'.xlsx', 'GR00', header=10)
                for year in np.arange(1982,2017):
                    dem.append(df[year].values)  
            elif region_name =='EL03': 
                print('Greece has incorrect region code ')
                df = pd.read_excel(dem_file_loc+'Demand_TimeSeries_'+scenario_capacity+'.xlsx', 'GR03', header=10)
                for year in np.arange(1982,2017):
                    dem.append(df[year].values)  
            else: 
                print('Tab not found in main document '+region_name)
                dem.append(np.zeros([8760,35]))
            
            
            
          
            
            
        DEM.append(np.array(dem).flatten())
        
        REGION_NAME.append(region_name)
    
    #%%
    # =============================================================================
    # Create a time index that is correct (no leap-days)
    # =============================================================================
    
    # now create dataframe for the data
    dftime = pd.DataFrame(index=pd.date_range("19820101","20161231T23", freq='H'))
                  
    # remove leapdays
    dftime = dftime[~((dftime.index.month == 2) & (dftime.index.day == 29))]              
                  
    
    #%%
       
    # out of the region loop we create new arrays with the info
    ds_save = xr.Dataset()
    ds_save['DEM']  = xr.DataArray(DEM, coords=[REGION_NAME, dftime.to_xarray().index], dims=["region", "time"])
    
    ds_save.to_netcdf(FOLDER_STORE+'ERA5_DEM_'+scenario_capacity+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
    
