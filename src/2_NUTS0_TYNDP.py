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
import os.path


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
            # '1979', '1980', '1981',
            # '1982', '1983', '1984',
            # '1985', '1986', '1987',
            # '1988', '1989', '1990',
            # '1991', '1992', '1993',
            # '1994', '1995', '1996',
            # '1997', '1998', '1999',

            # '2000', '2001', '2002',
            # '2003', '2004', '2005',
            # '2006', '2007', '2008',
            # '2009', '2010', '2011',
            # '2012', '2013', 
            '2014',
            '2015', '2016', '2017',
            '2018', '2019', 
            #'2020'            
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
PATH_TO_TYNDP = '/media/DataStager1/Other/CapacityDistribution/TYNDP/Origin/'

# Read NetCDF
FOLDER_ERA5_CF_NUTS0 = '/media/DataStager2/ERA5-EU_CF/NUTS0/'
FOLDER_EV_NUTS0 = '/media/DataStager2/ERA5-EU_EV/NUTS0/'


print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Load in the datafiles with the capacity distributions
# =============================================================================

# Select the distribution to run over
# capacity_distribution = CD_TYNDP_input[0]

for capacity_distribution in CD_TYNDP_input:

    print('NOTIFY: Working on Distribution '+capacity_distribution+'!')
    
    # Read in the Capacity Distribution from the TYNDP
    df_cd_tyndp = pd.read_csv(PATH_TO_TYNDP+'TYNDP-'+capacity_distribution+'.csv', sep=';', names=['Code', 'Type', 'Capacity'])
                                                                                                
    
    
    #%%
    # =============================================================================
    # Load in the NUTS0 data
    # =============================================================================
    
    # Set the year to run over
    for year in years:
        
        print('NOTIFY: Working on year '+year+'!')
        
        # Load in the NetCDF
        ds_cf_solar = xr.open_dataset(FOLDER_ERA5_CF_NUTS0+'ERA5-EU_CF-NUTS0_solar_'+str(year)+'.nc') #, chunks = {'time': 8760})
        ds_cf_windoff = xr.open_dataset(FOLDER_ERA5_CF_NUTS0+'ERA5-EU_CF-NUTS0_windoff_'+str(year)+'.nc') #, chunks = {'time': 8760})
        ds_cf_windon = xr.open_dataset(FOLDER_ERA5_CF_NUTS0+'ERA5-EU_CF-NUTS0_windon_'+str(year)+'.nc') #, chunks = {'time': 8760})
        
        
        #%%
        # =============================================================================
        # Multiply the capacity distribution with the capacity factor
        # =============================================================================
        
        # Set a new dataset for energy variables
        ds_ev_solar = xr.Dataset()
        ds_ev_windoff = xr.Dataset()
        ds_ev_windon = xr.Dataset()
        
        # The easy countries
        countries = [
            'BA', 'BE', 'DE', 
            'EE', 'ES', 'FI', 
            'HR', 'IE', 
            'LT', 'LU',
            'LV', 'NL', 'SI', 
            'AT', 'CH', 'CZ', 
            'HU', 'PL', 
            'PT', 'SK', 'TR', 
            'AL', 'BG', 'CY', 
            'ME', 'MK', 
            'RO', 'RS', 
            'MT', # to small but used offshore data for onshore figures (small capacity)
            'FR', # without the island of corsica
            'UK', # without the region of northern ireland 
            
            ]
        
        # The easy countries
        for country in countries: 
            
            #%% working on solar 
            # Define the capacity installed
            country_cap_distr_solar = df_cd_tyndp.where(df_cd_tyndp['Code'] == country).where(df_cd_tyndp['Type'] == 'Solar PV').dropna()['Capacity'].values
        
            # If this capacity is not defined, do not calculate
            if country_cap_distr_solar.size == 0:
                print('There is no solar capacity for '+country)
        
            # Apply the wind offshore capacity distribution        
            else: 
                # apply the cap distribution    
                ds_ev_solar[country] = country_cap_distr_solar * ds_cf_solar[country+'00']
                   
            #%% working on onshore wind 
            # Define the capacity installed
            country_cap_distr_windon = df_cd_tyndp.where(df_cd_tyndp['Code'] == country).where(df_cd_tyndp['Type'] == 'Onshore Wind').dropna()['Capacity'].values
        
            # If this capacity is not defined, do not calculate
            if country_cap_distr_windon.size == 0:
                print('There is no onshore wind capacity for '+country)
        
            # Apply the wind offshore capacity distribution        
            else: 
                # apply the cap distribution    
                ds_ev_windon[country] = country_cap_distr_windon * ds_cf_windon[country+'00']
        
                    
            #%% working on offshore wind 
            # Define the capacity installed
            country_cap_distr_windoff = df_cd_tyndp.where(df_cd_tyndp['Code'] == country).where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values
            
            # If this capacity is not defined, do not calculate
            if country_cap_distr_windoff.size == 0:
                print('There is no offshore capacity for '+country)
        
            # Apply the wind offshore capacity distribution        
            else: 
                ds_ev_windoff[country] = country_cap_distr_windoff * ds_cf_windoff[country+'00_OFF']
        
        
        #%%
        # =============================================================================
        # Working on Greece (just a naming issue)
        # =============================================================================
        country_cap_distr_windoff = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'EL').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values
            
        # If this capacity is not defined, do not calculate
        if country_cap_distr_windoff.size == 0:
            print('There is no offshore capacity for Greece')
        else: 
            ds_ev_windoff['EL'] = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'EL').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values * ds_cf_windoff['GR00_OFF']
        
        ds_ev_windon['EL'] = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'EL').where(df_cd_tyndp['Type'] == 'Onshore Wind').dropna()['Capacity'].values * ds_cf_windon['GR00']
        ds_ev_solar['EL'] = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'EL').where(df_cd_tyndp['Type'] == 'Solar PV').dropna()['Capacity'].values * ds_cf_solar['GR00']
            
        
        # =============================================================================
        # Working on Ukraine, without the oblast Moekatsjevo
        # =============================================================================
        ds_ev_windon['UA'] = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'UA').where(df_cd_tyndp['Type'] == 'Onshore Wind').dropna()['Capacity'].values * ds_cf_windon['UA02']
                
        
        # =============================================================================
        # Working on Sweden, capacity devided based on CF's of regions
        # =============================================================================
        
        # Determin the devisors 
        SE_devisor_windoff = ds_cf_windoff['SE01_OFF'].mean(...).values + ds_cf_windoff['SE02_OFF'].mean(...).values + ds_cf_windoff['SE03_OFF'].mean(...).values + ds_cf_windoff['SE04_OFF'].mean(...).values
        SE_devisor_windon = ds_cf_windon['SE01'].mean(...).values + ds_cf_windon['SE02'].mean(...).values + ds_cf_windon['SE03'].mean(...).values + ds_cf_windon['SE04'].mean(...).values
        SE_devisor_solar = ds_cf_solar['SE01'].mean(...).values + ds_cf_solar['SE02'].mean(...).values + ds_cf_solar['SE03'].mean(...).values + ds_cf_solar['SE04'].mean(...).values
        
        # Find the capacities
        SE_cap_off = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'SE').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values[0]
        SE_cap_on = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'SE').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values[0]
        SE_cap_sol = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'SE').where(df_cd_tyndp['Type'] == 'Solar PV').dropna()['Capacity'].values[0]
        
        # Calculate the regional energy generation for offshore wind
        SE01_off = SE_cap_off * ds_cf_windoff['SE01_OFF'] * ds_cf_windoff['SE01_OFF'].mean(...).values * SE_devisor_windoff**-1
        SE02_off = SE_cap_off * ds_cf_windoff['SE02_OFF'] * ds_cf_windoff['SE02_OFF'].mean(...).values * SE_devisor_windoff**-1
        SE03_off = SE_cap_off * ds_cf_windoff['SE03_OFF'] * ds_cf_windoff['SE03_OFF'].mean(...).values * SE_devisor_windoff**-1
        SE04_off = SE_cap_off * ds_cf_windoff['SE04_OFF'] * ds_cf_windoff['SE04_OFF'].mean(...).values * SE_devisor_windoff**-1
        # Sum over all regions to obtain national figures
        ds_ev_windoff['SE'] = SE01_off + SE02_off + SE03_off + SE04_off
        
        # Calculate the regional energy generation for onshore wind
        SE01_on = SE_cap_on * ds_cf_windon['SE01'] * ds_cf_windon['SE01'].mean(...).values * SE_devisor_windon**-1
        SE02_on = SE_cap_on * ds_cf_windon['SE02'] * ds_cf_windon['SE02'].mean(...).values * SE_devisor_windon**-1
        SE03_on = SE_cap_on * ds_cf_windon['SE03'] * ds_cf_windon['SE03'].mean(...).values * SE_devisor_windon**-1
        SE04_on = SE_cap_on * ds_cf_windon['SE04'] * ds_cf_windon['SE04'].mean(...).values * SE_devisor_windon**-1
        # Sum over all regions to obtain national figures
        ds_ev_windon['SE'] = SE01_on + SE02_on + SE03_on + SE04_on
        
        # Calculate the regional energy generation for solar PV
        SE01_sol = SE_cap_sol * ds_cf_solar['SE01'] * ds_cf_solar['SE01'].mean(...).values * SE_devisor_solar**-1
        SE02_sol = SE_cap_sol * ds_cf_solar['SE02'] * ds_cf_solar['SE02'].mean(...).values * SE_devisor_solar**-1
        SE03_sol = SE_cap_sol * ds_cf_solar['SE03'] * ds_cf_solar['SE03'].mean(...).values * SE_devisor_solar**-1
        SE04_sol = SE_cap_sol * ds_cf_solar['SE04'] * ds_cf_solar['SE04'].mean(...).values * SE_devisor_solar**-1
        # Sum over all regions to obtain national figures
        ds_ev_solar['SE'] = SE01_sol + SE02_sol + SE03_sol + SE04_sol
        
        
        
        
        # =============================================================================
        # Working on Norway
        # =============================================================================
        
        # Determin the devisors 
        NO_dev_on = ds_cf_windon['NOM1'].mean(...).values + ds_cf_windon['NON1'].mean(...).values + ds_cf_windon['NOS0'].mean(...).values
        NO_dev_sol = ds_cf_solar['NOM1'].mean(...).values + ds_cf_solar['NON1'].mean(...).values + ds_cf_solar['NOS0'].mean(...).values
        
        # Find the capacities
        NO_cap_on = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'NO').where(df_cd_tyndp['Type'] == 'Onshore Wind').dropna()['Capacity'].values[0]
        NO_cap_sol = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'NO').where(df_cd_tyndp['Type'] == 'Solar PV').dropna()['Capacity'].values[0]
        
        # Calculate the regional energy generation for offshore wind
        # If this capacity is not defined, do not calculate
        if df_cd_tyndp.where(df_cd_tyndp['Code'] == 'NO').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values.size == 0:
            print('There is no offshore capacity for Norway')
        else: 
            NO_cap_off = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'NO').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values[0]
            NO_dev_off = ds_cf_windoff['NOM1_OFF'].mean(...).values + ds_cf_windoff['NON1_OFF'].mean(...).values
            NOM1_off = NO_cap_off * ds_cf_windoff['NOM1_OFF'] * ds_cf_windoff['NOM1_OFF'].mean(...).values * NO_dev_off**-1
            NON1_off = NO_cap_off * ds_cf_windoff['NON1_OFF'] * ds_cf_windoff['NON1_OFF'].mean(...).values * NO_dev_off**-1
            # Sum over all regions to obtain national figures
            ds_ev_windoff['NO'] = NOM1_off + NON1_off
        
        # Calculate the regional energy generation for onshore wind
        NOM1_on = NO_cap_on * ds_cf_windon['NOM1'] * ds_cf_windon['NOM1'].mean(...).values * NO_dev_on**-1
        NON1_on = NO_cap_on * ds_cf_windon['NON1'] * ds_cf_windon['NON1'].mean(...).values * NO_dev_on**-1
        NOS0_on = NO_cap_on * ds_cf_windon['NOS0'] * ds_cf_windon['NOS0'].mean(...).values * NO_dev_on**-1
        # Sum over all regions to obtain national figures
        ds_ev_windon['NO'] = NOM1_on + NON1_on + NOS0_on
        
        # Calculate the regional energy generation for solar PV
        NOM1_sol = NO_cap_sol * ds_cf_solar['NOM1'] * ds_cf_solar['NOM1'].mean(...).values * NO_dev_sol**-1
        NON1_sol = NO_cap_sol * ds_cf_solar['NON1'] * ds_cf_solar['NON1'].mean(...).values * NO_dev_sol**-1
        NOS0_sol = NO_cap_sol * ds_cf_solar['NOS0'] * ds_cf_solar['NOS0'].mean(...).values * NO_dev_sol**-1
        # Sum over all regions to obtain national figures
        ds_ev_solar['NO'] = NOM1_sol + NON1_sol + NOS0_sol
        
        
        # =============================================================================
        # Working on Denmark
        # =============================================================================
        
        # Determin the devisors 
        DK_dev_off = ds_cf_windoff['DKE1_OFF'].mean(...).values + ds_cf_windoff['DKKF_OFF'].mean(...).values + ds_cf_windoff['DKW1_OFF'].mean(...).values
        DK_dev_on = ds_cf_windon['DKE1'].mean(...).values + ds_cf_windon['DKW1'].mean(...).values 
        DK_dev_sol = ds_cf_solar['DKE1'].mean(...).values + ds_cf_solar['DKW1'].mean(...).values
        
        # Find the capacities
        DK_cap_off = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'DK').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values[0]
        DK_cap_on = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'DK').where(df_cd_tyndp['Type'] == 'Onshore Wind').dropna()['Capacity'].values[0]
        DK_cap_sol = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'DK').where(df_cd_tyndp['Type'] == 'Solar PV').dropna()['Capacity'].values[0]
        
        # Calculate the regional energy generation for offshore wind
        DKE1_off = DK_cap_off * ds_cf_windoff['DKE1_OFF'] * ds_cf_windoff['DKE1_OFF'].mean(...).values * DK_dev_off**-1
        DKKF_off = DK_cap_off * ds_cf_windoff['DKKF_OFF'] * ds_cf_windoff['DKKF_OFF'].mean(...).values * DK_dev_off**-1
        DKW1_off = DK_cap_off * ds_cf_windoff['DKW1_OFF'] * ds_cf_windoff['DKW1_OFF'].mean(...).values * DK_dev_off**-1
        # Sum over all regions to obtain national figures
        ds_ev_windoff['DK'] = DKE1_off + DKKF_off + DKW1_off
        
        # Calculate the regional energy generation for onshore wind
        DKE1_on = DK_cap_on * ds_cf_windon['DKE1'] * ds_cf_windon['DKE1'].mean(...).values * DK_dev_on**-1
        DKW1_on = DK_cap_on * ds_cf_windon['DKW1'] * ds_cf_windon['DKW1'].mean(...).values * DK_dev_on**-1
        # Sum over all regions to obtain national figures
        ds_ev_windon['DK'] = DKE1_on + DKW1_on
        
        # Calculate the regional energy generation for solar PV
        DKE1_sol = DK_cap_sol * ds_cf_solar['DKE1'] * ds_cf_solar['DKE1'].mean(...).values * DK_dev_sol**-1
        DKW1_sol = DK_cap_sol * ds_cf_solar['DKW1'] * ds_cf_solar['DKW1'].mean(...).values * DK_dev_sol**-1
        # Sum over all regions to obtain national figures
        ds_ev_solar['DK'] = DKE1_sol + DKW1_sol
        
        
        
        # =============================================================================
        # Working on Italy
        # =============================================================================
        
        # Determin the devisors 
        IT_dev_on = ds_cf_windon['ITCA'].mean(...).values + ds_cf_windon['ITCN'].mean(...).values + ds_cf_windon['ITCS'].mean(...).values + ds_cf_windon['ITN1'].mean(...).values + ds_cf_windon['ITS1'].mean(...).values + ds_cf_windon['ITSA'].mean(...).values + ds_cf_windon['ITSI'].mean(...).values
        IT_dev_sol = ds_cf_solar['ITCA'].mean(...).values + ds_cf_solar['ITCN'].mean(...).values + ds_cf_solar['ITCS'].mean(...).values + ds_cf_solar['ITN1'].mean(...).values + ds_cf_solar['ITS1'].mean(...).values + ds_cf_solar['ITSA'].mean(...).values + ds_cf_solar['ITSI'].mean(...).values
        
        # Find the capacities
        IT_cap_on = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'IT').where(df_cd_tyndp['Type'] == 'Onshore Wind').dropna()['Capacity'].values[0]
        IT_cap_sol = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'IT').where(df_cd_tyndp['Type'] == 'Solar PV').dropna()['Capacity'].values[0]
        
        # Calculate the regional energy generation for offshore wind
        # If this capacity is not defined, do not calculate
        if df_cd_tyndp.where(df_cd_tyndp['Code'] == 'IT').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values.size == 0:
            print('There is no offshore capacity for Italy')
        else: 
            
            IT_dev_off = ds_cf_windoff['ITCA_OFF'].mean(...).values + ds_cf_windoff['ITCN_OFF'].mean(...).values + ds_cf_windoff['ITCS_OFF'].mean(...).values + ds_cf_windoff['ITN1_OFF'].mean(...).values + ds_cf_windoff['ITS1_OFF'].mean(...).values + ds_cf_windoff['ITSA_OFF'].mean(...).values + ds_cf_windoff['ITSI_OFF'].mean(...).values
            IT_cap_off = df_cd_tyndp.where(df_cd_tyndp['Code'] == 'IT').where(df_cd_tyndp['Type'] == 'Offshore Wind').dropna()['Capacity'].values[0]
            ITCA_off = IT_cap_off * ds_cf_windoff['ITCA_OFF'] * ds_cf_windoff['ITCA_OFF'].mean(...).values * IT_dev_off**-1
            ITCN_off = IT_cap_off * ds_cf_windoff['ITCN_OFF'] * ds_cf_windoff['ITCN_OFF'].mean(...).values * IT_dev_off**-1
            ITCS_off = IT_cap_off * ds_cf_windoff['ITCS_OFF'] * ds_cf_windoff['ITCS_OFF'].mean(...).values * IT_dev_off**-1
            ITN1_off = IT_cap_off * ds_cf_windoff['ITN1_OFF'] * ds_cf_windoff['ITN1_OFF'].mean(...).values * IT_dev_off**-1
            ITS1_off = IT_cap_off * ds_cf_windoff['ITS1_OFF'] * ds_cf_windoff['ITS1_OFF'].mean(...).values * IT_dev_off**-1
            ITSA_off = IT_cap_off * ds_cf_windoff['ITSA_OFF'] * ds_cf_windoff['ITSA_OFF'].mean(...).values * IT_dev_off**-1
            ITSI_off = IT_cap_off * ds_cf_windoff['ITSI_OFF'] * ds_cf_windoff['ITSI_OFF'].mean(...).values * IT_dev_off**-1
            # Sum over all regions to obtain national figures
            ds_ev_windoff['IT'] = ITCA_off + ITCN_off + ITCS_off + ITN1_off + ITS1_off + ITSA_off + ITSI_off
        
        # Calculate the regional energy generation for onshore wind
        ITCA_on = IT_cap_on * ds_cf_windon['ITCA'] * ds_cf_windon['ITCA'].mean(...).values * IT_dev_on**-1
        ITCN_on = IT_cap_on * ds_cf_windon['ITCN'] * ds_cf_windon['ITCN'].mean(...).values * IT_dev_on**-1
        ITCS_on = IT_cap_on * ds_cf_windon['ITCS'] * ds_cf_windon['ITCS'].mean(...).values * IT_dev_on**-1
        ITN1_on = IT_cap_on * ds_cf_windon['ITN1'] * ds_cf_windon['ITN1'].mean(...).values * IT_dev_on**-1
        ITS1_on = IT_cap_on * ds_cf_windon['ITS1'] * ds_cf_windon['ITS1'].mean(...).values * IT_dev_on**-1
        ITSA_on = IT_cap_on * ds_cf_windon['ITSA'] * ds_cf_windon['ITSA'].mean(...).values * IT_dev_on**-1
        ITSI_on = IT_cap_on * ds_cf_windon['ITSI'] * ds_cf_windon['ITSI'].mean(...).values * IT_dev_on**-1
        # Sum over all regions to obtain national figures
        ds_ev_windon['IT'] = ITCA_on + ITCN_on + ITCS_on + ITN1_on + ITS1_on + ITSA_on + ITSI_on
        
        # Calculate the regional energy generation for solar PV
        ITCA_sol = IT_cap_sol * ds_cf_solar['ITCA'] * ds_cf_solar['ITCA'].mean(...).values * IT_dev_sol**-1
        ITCN_sol = IT_cap_sol * ds_cf_solar['ITCN'] * ds_cf_solar['ITCN'].mean(...).values * IT_dev_sol**-1
        ITCS_sol = IT_cap_sol * ds_cf_solar['ITCS'] * ds_cf_solar['ITCS'].mean(...).values * IT_dev_sol**-1
        ITN1_sol = IT_cap_sol * ds_cf_solar['ITN1'] * ds_cf_solar['ITN1'].mean(...).values * IT_dev_sol**-1
        ITS1_sol = IT_cap_sol * ds_cf_solar['ITS1'] * ds_cf_solar['ITS1'].mean(...).values * IT_dev_sol**-1
        ITSA_sol = IT_cap_sol * ds_cf_solar['ITSA'] * ds_cf_solar['ITSA'].mean(...).values * IT_dev_sol**-1
        ITSI_sol = IT_cap_sol * ds_cf_solar['ITSI'] * ds_cf_solar['ITSI'].mean(...).values * IT_dev_sol**-1
        # Sum over all regions to obtain national figures
        ds_ev_solar['IT'] = ITCA_sol + ITCN_sol + ITCS_sol + ITN1_sol + ITS1_sol + ITSA_sol + ITSI_sol
        
        
        #%%
        # =============================================================================
        # Time to save the data
        # =============================================================================
        
        # Setting the general dataset attributes
        ds_ev_windoff.attrs.update(
            author = 'Laurens Stoop UU/KNMI/TenneT',
            variables = 'Wind offshore electricity generation for a certain region',
            units = 'MWh',
            created = datetime.datetime.today().strftime('%d-%m-%Y'),
            region_definition = 'ENTSO-E StudyZones at national level aggregated',
            CapacityDistribution = 'TYNDP-'+capacity_distribution,
            data_source = 'Capacity factors based on ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [31-05-2021]'
            )
        
        # copy most and update partially
        ds_ev_windon.attrs = ds_ev_windoff.attrs
        ds_ev_windon.attrs.update(
             variables = 'Wind onshore electricity generation for a certain region',
            )
        
        ds_ev_solar.attrs = ds_ev_windoff.attrs
        ds_ev_solar.attrs.update(
             variables = 'Solar PV electricity generation for a certain region',
            )
        
        
        
        # Saving the files as NetCDF
        ds_ev_windoff.to_netcdf(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WOF_'+str(year)+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
        ds_ev_windon.to_netcdf(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WON_'+str(year)+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
        ds_ev_solar.to_netcdf(FOLDER_EV_NUTS0+capacity_distribution+'/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_SPV_'+str(year)+'.nc', encoding={'time':{'units':'days since 1900-01-01'}})
        
        # Converting ot Pandas
        df_windoff = ds_ev_windoff.to_pandas()
        df_windon = ds_ev_windon.to_pandas()
        df_solar = ds_ev_solar.to_pandas()
        
        # Saving as CSV
        df_windoff.to_csv(FOLDER_EV_NUTS0+'csv/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WOF_'+str(year)+'.csv')
        df_windon.to_csv(FOLDER_EV_NUTS0+'csv/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_WON_'+str(year)+'.csv')
        df_solar.to_csv(FOLDER_EV_NUTS0+'csv/ERA5-EU_EV_TYNDP-'+capacity_distribution+'_SPV_'+str(year)+'.csv')
