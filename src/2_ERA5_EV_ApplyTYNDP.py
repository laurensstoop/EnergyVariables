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
FOLDER_CF_MZ = '/media/DataStager2/ERA5_CF_MZ/'
FOLDER_EV = '/media/DataStager2/ERA5_EV/'
# Set the path for the data
PATH_TO_TYNDP = '/media/DataStager1/Other/CapacityDistribution/TYNDP/Originv3/'

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
            '1988', '1989', '1990',
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

#%%
# =============================================================================
# Set the specifics to run over 
# =============================================================================

# Set the year to run over
for year in years:
    
    print('NOTIFY: Working on year '+year+'!')
    
    #%%
    # =============================================================================
    # Loading the EV & PECD data
    # =============================================================================
    
    # EV versions 
    dsW = xr.open_dataset(FOLDER_CF_MZ+'ERA5_CF_MZ_WM_'+year+'.nc')
    
    #Fix a few naming issues
    region_name_fix= [
            'SE04_OFF', 'SE03_OFF', 'CY00_OFF', 'MT00', 'ITSI', 'LB00', 'PL00', # MT00_OFF -> MT00
            'LT00', 'DKKF', 'ITCN_OFF', 'LU00', 'NL00_OFF', 'FR00_OFF', 
            'FI00_OFF', 'BG00', 'BG00_OFF', 'MA00_OFF', 'NOM1_OFF', 'NON1', 'CZ00',
            'SK00', 'CH00', 'IE00_OFF', 'SY00', 'UKNI_OFF', 'TN00_OFF', 'FR15',
            'RS00', 'ITN1_OFF', 'NOS0', 'IE00', 'DE00', 'AT00', 'EL00_OFF', # GR00_OFF -> EL00_OFF
            'DKE1_OFF', 'MD00', 'ES00', 'AL00', 'SY00_OFF', 'NOS0_OFF', 'HR00_OFF',
            'UA02_OFF', 'RO00', 'PT00_OFF', 'ME00', 'HR00', 'DBOT_OFF', 'DKE1',
            'LV00', 'NL00', 'TR00', 'NON1_OFF', 'TR00_OFF', 'ITCS_OFF', 'DBUK_OFF',
            'RO00_OFF', 'MA00', 'EL00', 'EL03', 'IL00_OFF', 'TN00', 'EG00', 'UA01', # GR00/GR03 -> EL00/EL03
            'UA02', 'BE00', 'PL00_OFF', 'ITSA_OFF', 'MK00', 'SE02_OFF', 'SE01_OFF',
            'ITN1', 'PT00', 'DE00_OFF', 'AL00_OFF', 'DKW1', 'LV00_OFF', 'BE00_OFF',
            'EE00_OFF', 'EG00_OFF', 'UK00', 'BA00', 'SI00', 'UK00_OFF', 'DZ00',
            'IL00', 'ME00_OFF', 'CY00', 'UKNI', 'DKW1_OFF', 'LT00_OFF', 'DZ00_OFF',
            'NOM1', 'FI00', 'LY00', 'EE00', 'SE01', 'FR00', 'SE02', 'ES00_OFF',
            'SE03', 'SE04', 'LY00_OFF', 'HU00', 'ITSA', 'ITSI_OFF', 'LB00_OFF',
            'ITCA', 'ITCN', 'ITCS', 'ITS1', 'ITS1_OFF', 'ITCA_OFF' ]
    dsW['region'] = region_name_fix



    #%%
    # =============================================================================
    # Load in the datafiles with the capacity distributions
    # =============================================================================
    
    # Select the distribution to run over
    for scenario_capacity in TYNDP_scenarios_capacity:
    
        print('      :'+scenario_capacity)
        # Open the scenario to use
        dfC = pd.read_csv(PATH_TO_TYNDP+'TYNDP-'+scenario_capacity+'.csv' ) 
        
        # Read the index, Transpose, convert to xarray Set the index nicely
        dsC = dfC.set_index('Country').transpose().to_xarray()
        dsC = dsC.rename({'index':'region'})
        
        
        
        
        #%%
        # =============================================================================
        # Calculate the Production of Energy from RES
        # =============================================================================
        
        # Preset a dataset & temp arrays
        dsP = xr.Dataset()
        pspv=[]
        pwon=[]
        pwof=[]
        REGION_NAME1=[]
        REGION_NAME2=[]
        
        # Select a region (the Netherlands is 12/54 in NUTS0)
        for REGION in dsC.region.values:
            
            # When a offshore region exist, we also calculate it, otherwise we leave it out  
            if REGION == 'DKKF':
                pwof.append(dsW.WOF.sel(region = REGION) * dsC.OffshoreWind.sel(region=REGION))
                
                REGION_NAME2.append(REGION)
            
            elif REGION+'_OFF' in dsW.region:
                
                # Calculate the output by combining the CF & capacity
                pwof.append(dsW.WOF.sel(region = REGION+'_OFF') * dsC.OffshoreWind.sel(region=REGION))
                pwon.append(dsW.WON.sel(region = REGION) * dsC.OnshoreWind.sel(region=REGION))
                pspv.append(dsW.SPV.sel(region = REGION) * dsC.SolarPV.sel(region=REGION))
                
                # keeping track of coordinates
                REGION_NAME1.append(REGION)
                REGION_NAME2.append(REGION)
            else:
                # Calculate the output by combining the CF & capacity
                pwon.append(dsW.WON.sel(region = REGION) * dsC.OnshoreWind.sel(region=REGION))
                pspv.append(dsW.SPV.sel(region = REGION) * dsC.SolarPV.sel(region=REGION))
                # keeping track of coordinates
                REGION_NAME1.append(REGION)
        
        # out of the region loop we create new arrays with the info
        dsT1 = xr.Dataset()
        dsT2 = xr.Dataset()
        dsT1['PWON']  = xr.DataArray(pwon, coords=[REGION_NAME1, dsW.time], dims=["region", "time"])
        dsT1['PSPV']  = xr.DataArray(pspv, coords=[REGION_NAME1, dsW.time], dims=["region", "time"])
        dsT2['PWOF']  = xr.DataArray(pwof, coords=[REGION_NAME2, dsW.time], dims=["region", "time"])
        
        # now we combine the data & fill the gaps with 0
        dsN = xr.merge([dsT1, dsT2])
        dsN = dsN.fillna(0)
                
        
        #%%
        # =============================================================================
        # Save the data
        # =============================================================================
        
        # dataset attributes
        dsN.attrs.update(
            author = 'Laurens Stoop UU/KNMI/TenneT',
            created = datetime.datetime.today().strftime('%d-%m-%Y'),
            map_area = 'Europe',
            region_definition = 'ENTSO-E Marketzones',
            TYNDP_scenario = scenario_capacity,
            data_source = 'Power generation based on ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [28-02-2022]'
            )
        
        # variable attributes 
        dsN.PWON.attrs.update(
            variable = 'Wind onshore electricity generation',
            units = 'MWh'
            )
        dsN.PWOF.attrs.update(
            variable = 'Wind offshore electricity generation',
            units = 'MWh'
            )        
        dsN.PSPV.attrs.update(
            variable = 'Solar PV electricity generation',
            units = 'MWh'
            )
        
        
        # Saving the file
        dsN.to_netcdf(FOLDER_EV+'ERA5_EV_'+scenario_capacity+'_'+year+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
        
        dsN.PWOF.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_WOF_'+scenario_capacity+'_'+year+'.csv')
        dsN.PWON.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_WON_'+scenario_capacity+'_'+year+'.csv')
        dsN.PSPV.to_pandas().transpose().to_csv(FOLDER_EV+'csv/ERA5_EV_SPV_'+scenario_capacity+'_'+year+'.csv')
