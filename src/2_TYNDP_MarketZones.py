#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remade on Sun 30 May 2021 22:32

@author: Laurens Stoop - l.p.stoop@uu.nl

"""

#%%
# =============================================================================
# Dependencies
# =============================================================================


## Importing modules
import xarray as xr 
import numpy as np
# import regionmask
# import geopandas as gpd
import datetime
import pandas as pd
# import matplotlib.pyplot as plt
# import os.path


# Select the years to run
years = np.array([
            # '1950', '1951', '1952',
            # '1953', '1954', '1955',
            # '1956', '1957', '1958',
            # '1959', '1960', '1961',
            # '1962', '1963', '1964',
            # '1965', '1966', '1967',
            # '1968', '1969', '1970',
            # '1971', '1972', '1973',
            # '1974', '1975', '1976',
            # '1977', '1978',
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
            '2012', '2013', 
            '2014',
            '2015', '2016', '2017',
            '2018', '2019', 
            '2020'            
        ])


# Versions of the TYNDP
CD_TYNDP_input = np.array([
            'DE_2030', 
            'DE_2040',
            'GA_2030', 
            'GA_2040', 
            'NT_2025', 
            'NT_2030', 
            'NT_2040'
        ])


# Set the path for the data
PATH_TO_TYNDP = '/media/DataStager1/Other/CapacityDistribution/TYNDP/Originv3/'

# Read NetCDF
FOLDER_ERA5_CF_NUTS0 = '/media/DataStager2/ERA5-EU_CF/MarketZones/'
FOLDER_EV_NUTS0 = '/media/DataStager2/ERA5-EU_EV/MarketZones/'


print('NOTIFY: Initialization is complete, Skynet active')
    
    
        
#%%
# =============================================================================
# Load in the MarketZone data
# =============================================================================

# Set the year to run over
for year in years:
    
    print('NOTIFY: Working on year '+year+'!')
    
    # Load in the NetCDF
    ds_cf_solar = xr.open_dataset(FOLDER_ERA5_CF_NUTS0+'ERA5-EU_CF-MarketZones_solar_'+str(year)+'.nc') #, chunks = {'time': 8760})
    ds_cf_windoff = xr.open_dataset(FOLDER_ERA5_CF_NUTS0+'ERA5-EU_CF-MarketZones_windoff_'+str(year)+'.nc') #, chunks = {'time': 8760})
    ds_cf_windon = xr.open_dataset(FOLDER_ERA5_CF_NUTS0+'ERA5-EU_CF-MarketZones_windon_'+str(year)+'.nc') #, chunks = {'time': 8760})
    
    #%%
    # =============================================================================
    # Load in the datafiles with the capacity distributions
    # =============================================================================
    
    # Select the distribution to run over
    # capacity_distribution = CD_TYNDP_input[0]
    
    for capacity_distribution in CD_TYNDP_input:
    
        print('NOTIFY: Working on Distribution '+capacity_distribution+'!')
        
        # Read in the Capacity Distribution from the TYNDP
        df_cd_tyndp = pd.read_csv(PATH_TO_TYNDP+'TYNDP-'+capacity_distribution+'.csv' ) 
                                                                     
        # Set the index nicely                               
        df_cd_tyndp  = df_cd_tyndp.set_index('Country')
        
        # now transpose the data
        df_cd_tyndp = df_cd_tyndp.transpose()   
     
        #%%
        # =============================================================================
        # Multiply the capacity distribution with the capacity factor
        # =============================================================================
        
        # Set a new dataset for energy variables
        ds_ev_solar = xr.Dataset()
        ds_ev_windoff = xr.Dataset()
        ds_ev_windon = xr.Dataset()
        
        
        # The countries we now loop
        for country in df_cd_tyndp.index: 
               
            
            #%% working on solar 
            # Define the capacity installed
            country_cap_distr_solar = df_cd_tyndp.loc[country].loc['Solar PV']
        
            # If this capacity is not defined, do not calculate
            if country_cap_distr_solar.size == 0 or country_cap_distr_solar == 0:
                print('There is no solar capacity for '+country)
                
            # Fix the Greek names to international standard                
            elif country == 'EL00':
                ds_ev_solar[country] = country_cap_distr_solar * ds_cf_solar['GR00']
            elif country == 'EL03':
                ds_ev_solar[country] = country_cap_distr_solar * ds_cf_solar['GR03']
            
            # Fix luxembour (somehow it is called LUG/LUF/LUB) 
            elif country == 'LUG1':
                ds_ev_solar['LU00'] = df_cd_tyndp.loc['LUG1'].loc['Solar PV'] * ds_cf_solar['LU00'] 
            
            # Apply the wind offshore capacity distribution        
            else: 
                # apply the cap distribution    
                ds_ev_solar[country] = country_cap_distr_solar * ds_cf_solar[country]
                   
            #%% working on onshore wind 
            # Define the capacity installed
            country_cap_distr_windon = df_cd_tyndp.loc[country].loc['Onshore Wind']
        
            # If this capacity is not defined, do not calculate
            if country_cap_distr_windon.size == 0 or country_cap_distr_windon == 0:
                print('There is no onshore wind capacity for '+country)
            
            # Fix the Greek names to international standard                
            elif country == 'EL00':
                ds_ev_windon[country] = country_cap_distr_windon * ds_cf_windon['GR00']
            elif country == 'EL03':
                ds_ev_windon[country] = country_cap_distr_windon * ds_cf_windon['GR03']
            
            # Fix luxembour (somehow it is called LUG/LUF/LUB)
            elif country == 'LUG1':
                ds_ev_windon['LU00'] = df_cd_tyndp.loc['LUG1'].loc['Onshore Wind'] * ds_cf_windon['LU00']
                        
            # Apply the wind offshore capacity distribution        
            else: 
                # apply the cap distribution    
                ds_ev_windon[country] = country_cap_distr_windon * ds_cf_windon[country]
        
                    
            #%% working on offshore wind 
            # Define the capacity installed
            country_cap_distr_windoff = df_cd_tyndp.loc[country].loc['Offshore Wind']
            
            # If this capacity is not defined, do not calculate
            if country_cap_distr_windoff.size == 0 or country_cap_distr_windoff == 0:
                print('There is no offshore capacity for '+country)
        
            # Fix the small easternly Danish region
            elif country == 'DEKF':
                ds_ev_windoff[country] = country_cap_distr_windoff * ds_cf_windoff['DE00_OFF']
        
            # Fix the Greek names to international standard                
            elif country == 'EL00':
                ds_ev_windoff[country] = country_cap_distr_windoff * ds_cf_windoff['GR00_OFF']
            elif country == 'EL03':
                ds_ev_windoff[country] = country_cap_distr_windoff * ds_cf_windoff['GR00_OFF']
            
           # Apply the wind offshore capacity distribution        
            else: 
                ds_ev_windoff[country] = country_cap_distr_windoff * ds_cf_windoff[country+'_OFF']
        
        
        
        #%%
        # =============================================================================
        # Time to save the data
        # =============================================================================
        
        # Setting the general dataset attributes
        ds_ev_windoff.attrs.update(
            author = 'Laurens Stoop UU/KNMI/TenneT',
            variables = 'Wind offshore electricity generation',
            units = 'MWh',
            created = datetime.datetime.today().strftime('%d-%m-%Y'),
            region_definition = 'ENTSO-E MarketZones',
            CapacityDistribution = 'TYNDP-'+capacity_distribution,
            data_source = 'Energy production variables based on TYNDP scenarios and ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [31-05-2021]'
            )
        
        # copy most and update partially
        ds_ev_windon.attrs = ds_ev_windoff.attrs
        ds_ev_windon.attrs.update(
              variables = 'Wind onshore electricity generation',
            )
        
        ds_ev_solar.attrs = ds_ev_windoff.attrs
        ds_ev_solar.attrs.update(
              variables = 'Solar PV electricity generation',
            )
        
        
        
        # Saving the files as NetCDF
        # ds_ev_windoff.to_netcdf(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WOF_'+str(year)+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
        # ds_ev_windon.to_netcdf(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WON_'+str(year)+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
        # ds_ev_solar.to_netcdf(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_SPV_'+str(year)+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
        
        # Converting ot Pandas
        df_windoff = ds_ev_windoff.to_pandas()
        df_windon = ds_ev_windon.to_pandas()
        df_solar = ds_ev_solar.to_pandas()
        
        # Saving as CSV
        df_windoff.to_csv(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WOF_'+str(year)+'.csv')
        df_windon.to_csv(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WON_'+str(year)+'.csv')
        df_solar.to_csv(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_SPV_'+str(year)+'.csv')
