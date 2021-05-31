#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restructered on Sun 30 May 2021 17:04

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
# import pandas as pd
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
            '2000', '2001', '2002',
            '2003', '2004', '2005',
            '2006', '2007', '2008',
            '2009', '2010', '2011',
            '2012', '2013', '2014',
            '2015', '2016', '2017',
            '2018', '2019', '2020'            
        ])


# Set the path for the data
PATH_TO_NUTS0 = '/media/DataStager1/Other/RegionDefinitions/ENTSO-E_StudyZones/DTU-PECD22-Polygons_SZ_VF2021.shp'
# PATH_TO_NUTS1 = '/media/DataStager1/Other/RegionDefinitions/ENTSO-E_StudyZones/DTU-PECD22-Polygons_VF2021.shp'

# Read NetCDF
FOLDER_WITH_NETCDF = '/media/DataStager2/ERA5-EU_CF/'
FOLDER_STORE = '/media/DataStager2/ERA5-EU_CF/NUTS0/'


print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Load in the base shapefile 
# =============================================================================

# Load the shapefile
nuts0 = gpd.read_file(PATH_TO_NUTS0)
# nuts1 = gpd.read_file(PATH_TO_NUTS1)

# There are regions we do not consider
not_considered_nuts0 = [
    'JO00', 'JO00_OFF',  # Jordany
    'MA00', 'MA00_OFF',  # Marocco
    'SY00', 'SY00_OFF',  # Syria
    'TN00', 'TN00_OFF',  # Tunisia
    'IS00', 'IS00_OFF',  # Iceland
    'IL00', 'IL00_OFF',  # Israel
    'PS00', 'PS00_OFF',  # Palistine & Gaza
    'EG00', 'EG00_OFF',  # Egypt
    'DZ00', 'DZ00_OFF',  # Algeria
    'LY00', 'LY00_OFF',  # Libya
    # Regions not considered resolution or model constrains
    'SI00_OFF',  # Slovenia offshore is to small for ERA5 data
    'BA00_OFF',  # Bosnia and Herzegovina offshore region to small for ERA5 data 
    'MT00',  # Malta is to small for data on the island
    ]

# Now set all nuts0 regions we do not consider to NaN's
for NC in not_considered_nuts0: 
    nuts0 = nuts0.where(nuts0['Study Zone'] != NC)

# Removal of all NaN's from the table     
nuts0 = nuts0.dropna()


# There is an empty LY00 zone in there 
# nuts1.iloc[246]
# nuts1 = nuts1.drop(index=246)

# To check some info you could read the headers of the shapefiles
# nuts0.head() # to check the contents      --> 121 on-/offshore definitions
# nuts1.head() # to check the contents      --> 262 on-/offshore definitions


#%%
# =============================================================================
# Load in the datafiles them self
# =============================================================================

# The mega loop
for year in years:

    # Define the file name
    file_save_solar = FOLDER_STORE+'ERA5-EU_CF-NUTS0_solar_'+str(year)+'.nc'
    file_save_windoff = FOLDER_STORE+'ERA5-EU_CF-NUTS0_windoff_'+str(year)+'.nc'
    file_save_windon = FOLDER_STORE+'ERA5-EU_CF-NUTS0_windon_'+str(year)+'.nc'
    
    
    # Check if file allready exist, then get out
    if os.path.isfile(file_save_windon) == True:
        
        # Tell us the file exist
        print('NOTIFY: Allready applied for year '+year+'!')
      
        
    # IF the file doesn't exist, apply the distribution
    elif os.path.isfile(file_save_windon) == False:
        
        print('NOTIFY: Working on year '+year+'!')
        
        # Load in the NetCDF
        ds = xr.open_mfdataset(FOLDER_WITH_NETCDF+'ERA5-EU_CF_'+str(year)+'.nc') #, chunks = {'time': 8760})
        
        #%%
        # =============================================================================
        # Now we define the regionmask and to later apply it
        # =============================================================================
        
        # CALCULATE MASK
        SZ0_mask_poly = regionmask.Regions(name = 'ENTSO-E_StudyZone0_Mask', numbers = np.arange(0,len(nuts0)), abbrevs = list(nuts0['Study Zone']), outlines = list(nuts0.geometry.values[i] for i in np.arange(0,len(nuts0)))) # names = list(nuts0['Study Zone']),
        # SZ1_mask_poly = regionmask.Regions(name = 'ENTSO-E_StudyZone1_Mask', numbers = list(range(0,262)), abbrevs = list(nuts1['Code']), outlines = list(nuts1.geometry.values[i] for i in range(0,262))) # names = list(nuts1['Study Zone']),
        # print(nuts_mask_poly)
        
        # Create the mask
        mask = SZ0_mask_poly.mask(ds.isel(time = 0), method = None)
        # mask = SZ0_mask_poly.mask(ds.isel(time = 0), method = None)
        # mask # To check the contents of the mask defined
        
        
        #%%
        # =============================================================================
        # Now selecting a region to select the data
        # =============================================================================
        
        # Prepare a dataset for filling with regional mean data
        ds_solarCF = xr.Dataset()
        ds_windCF_off = xr.Dataset()
        ds_windCF_on = xr.Dataset()
        
        # Select a region (the Netherlands is 12/54 in NUTS0)
        for ID_REGION in np.arange(0,len(nuts0)):
            
            # Determine the region name
            region_name = nuts0.iloc[ID_REGION]['Study Zone']

            print('######: working on region '+region_name+' ('+str(ID_REGION)+'/98) !')
            
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
            
            # # =============================================================================
            # # A quick figure for the sanity checks
            # # =============================================================================
            # plt.figure(figsize=(12,8))
            # ax = plt.axes()
            # out_sel.solarCF.isel(time = 4140).plot(ax = ax)
            # nuts0.plot(ax = ax, alpha = 0.8, facecolor = 'none')
                        
            
            #%%
            # =============================================================================
            # Regional mean for saving data
            # =============================================================================
                        
            # Offshore region only have wind 
            if region_name == 'MT00_OFF':
                
                # fixing the to small region for Malta where we do need data
                ds_windCF_off[region_name] = out_sel.windCF_off.groupby('time').mean(...)
                ds_windCF_on['MT00'] = out_sel.windCF_on.groupby('time').mean(...)
                ds_solarCF['MT00'] = out_sel.solarCF.groupby('time').mean(...)
                
            elif region_name[-4:] == '_OFF':
                
                # Save the regional mean into the main dataset under the region's name
                ds_windCF_off[region_name] = out_sel.windCF_off.groupby('time').mean(...)
                
            # Non-offshore regions have wind and solar installed               
            else:  
                
                # Save the regional mean of the onshore wind and solar CF's
                ds_windCF_on[region_name] = out_sel.windCF_on.groupby('time').mean(...)
                ds_solarCF[region_name] = out_sel.solarCF.groupby('time').mean(...)
                
        #%%                
        # =============================================================================
        # Setting units & saving
        # =============================================================================
               
        # Setting the general dataset attributes
        ds_solarCF.attrs.update(
            author = 'Laurens Stoop UU/KNMI/TenneT',
            variables = 'Solar PH capacity factor for a specific region',
            units = '[0-1]',
            created = datetime.datetime.today().strftime('%d-%m-%Y'),
            map_area = 'Europe',
            region_definition = 'ENTSO-E StudyZones at national level aggregated',
            data_source = 'Capacity factors based on ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [31-05-2021]'
            )
        
        # Setting the general dataset attributes
        ds_windCF_off.attrs.update(
            author = 'Laurens Stoop UU/KNMI/TenneT',
            variables = 'Wind Offshore capacity factor for a specific region',
            units = '[0-1]',
            created = datetime.datetime.today().strftime('%d-%m-%Y'),
            map_area = 'Europe',
            region_definition = 'ENTSO-E StudyZones at national level aggregated',
            data_source = 'Capacity factors based on ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [31-05-2021]'
            )
        
        # Setting the general dataset attributes
        ds_windCF_on.attrs.update(
            author = 'Laurens Stoop UU/KNMI/TenneT',
            variables = 'Wind onshore capacity factor for a specific region',
            units = '[0-1]',
            created = datetime.datetime.today().strftime('%d-%m-%Y'),
            map_area = 'Europe',
            region_definition = 'ENTSO-E StudyZones at national level aggregated',
            data_source = 'Capacity factors based on ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [31-05-2021]'
            )
        
        # Saving the file
        ds_solarCF.to_netcdf(file_save_solar, encoding={'time':{'units':'days since 1900-01-01'}})
        ds_windCF_off.to_netcdf(file_save_windoff, encoding={'time':{'units':'days since 1900-01-01'}})
        ds_windCF_on.to_netcdf(file_save_windon, encoding={'time':{'units':'days since 1900-01-01'}})

