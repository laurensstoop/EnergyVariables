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
            # '1979', '1980', '1981',
            # '1982', '1983', '1984',
            # '1985', '1986', '1987',
            # '1988', '1989', 
            # '1990',
            # '1991', '1992', '1993',
            # '1994', '1995', '1996',
            # '1997', '1998', '1999',
            # '2000', '2001', '2002',
            # '2003', '2004', '2005',
            # '2006', '2007', '2008',
            # '2009', '2010', '2011',
            # '2012', '2013', '2014',
            # '2015', '2016', '2017',
            # '2018', '2019', 
            # '2020'            
        ])


# Set the path for the data
PATH_TO_NUTS0 = '/media/DataStager1/Other/RegionDefinitions/ENTSO-E_StudyZones/DTU-PECD22-Polygons_SZ_VF2021.shp'
# PATH_TO_NUTS1 = '/media/DataStager1/Other/RegionDefinitions/ENTSO-E_StudyZones/DTU-PECD22-Polygons_VF2021.shp'



# Read NetCDF
# FOLDER_WITH_NETCDF = '/media/DataGate2/ERA5/BASE2/'
FOLDER_WITH_NETCDF = '/media/DataStager2/ERA5_BASE2_t2m/'
FOLDER_STORE = '/media/DataStager2/ERA5_LoadModel/'


# =============================================================================
# Open population & demand
# =============================================================================

# open the population file & select 2020
# Terminal job: cdo -select,timestep=1,2,3,4,5 gpw_v4_population_count_rev11_ERA5-remapcon.nc GPW_ERA5_data-only.nc
pop_file = '/media/DataStager1/Other/PopulationGDP/GPDW_v4/GPW_ERA5_data-only.nc'
dsp = xr.open_dataset(pop_file) #(2000, 2005, 2010, 2015, 2020, [Not important variables])
dsp = dsp.rename({'Population Count, v4.11 (2000, 2005, 2010, 2015, 2020): 2.5 arc-minutes' : 'pop'} )
dsp = dsp.isel(time=4).reset_coords().drop('time')
dsp = dsp.rename({'longitude': 'lon','latitude': 'lat'})


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
    # 'MA00', 'MA00_OFF',  # Marocco
    # 'SY00', 'SY00_OFF',  # Syria
    # 'TN00', 'TN00_OFF',  # Tunisia
    'IS00', 'IS00_OFF',  # Iceland
    # 'IL00', 'IL00_OFF',  # Israel
    'PS00', 'PS00_OFF',  # Palistine & Gaza
    # 'EG00', 'EG00_OFF',  # Egypt
    # 'DZ00', 'DZ00_OFF',  # Algeria
    # 'LY00', 'LY00_OFF',  # Libya
#
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


# # There is an empty LY00 zone in there 
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
    # for month in ['01']: #, '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
   
        # Define the file name
        # file_save = FOLDER_STORE+'ERA5_PWT_'+year+month+'.nc'        
        file_save = FOLDER_STORE+'ERA5_PWT_'+year+'.nc'        
            
            
        # Check if file allready exist, then get out
        if os.path.isfile(file_save) == True:
            
            # Tell us the file exist
            print('NOTIFY: Allready applied for year '+year+'!')
          
            
        # IF the file doesn't exist, apply the distribution
        elif os.path.isfile(file_save) == False:
            
            print('NOTIFY: Working on year '+year+'!')
            
            # Load in the NetCDF
            ds = xr.open_mfdataset(FOLDER_WITH_NETCDF+'ERA5-EU_'+year+'*.nc') #, chunks = {'time': 8760})
            # ds = xr.open_dataset(FOLDER_WITH_NETCDF+'ERA5-EU_'+year+month+'.nc') #, chunks = {'time': 8760})
            
            # remaming the coordinates
            ds = ds.rename({'longitude': 'lon','latitude': 'lat'})
            ds['t2m'] = ds.t2m - 273.4
            
            # Adding the population based weights
            weights_pop = dsp.pop.fillna(0)
            weights_pop.name = 'weights'
            
            
            #%%
            # =============================================================================
            # Now we define the regionmask and to later apply it
            # =============================================================================
            
            # CALCULATE MASK
            SZ0_mask_poly = regionmask.Regions(name = 'ENTSO-E_StudyZone0_Mask', numbers = np.arange(0,len(nuts0)), abbrevs = list(nuts0['Study Zone']), outlines = list(nuts0.geometry.values[i] for i in np.arange(0,len(nuts0)))) # names = list(nuts0['Study Zone']),
            # SZ1_mask_poly = regionmask.Regions(name = 'ENTSO-E_StudyZone1_Mask', numbers = np.arange(0,len(nuts1)), abbrevs = list(nuts1['Code']), outlines = list(nuts1.geometry.values[i] for i in np.arange(0,len(nuts0)))) # names = list(nuts1['Study Zone']),        # print(nuts_mask_poly)
            
            # Create the mask
            mask = SZ0_mask_poly.mask(ds.isel(time = 0), method = None)
            # mask = SZ1_mask_poly.mask(ds.isel(time = 0), method = None)
            # mask # To check the contents of the mask defined
            
            
            #%%
            # =============================================================================
            # Now selecting a region to select the data
            # =============================================================================
            
            # Prepare a dataset for filling with regional population weighted mean t2m data
            PWT=[]
            REGION_NAME=[]
            
            # Select a region (the Netherlands is 12/54 in NUTS0)
            for ID_REGION in np.arange(0,len(nuts0)):
            # for ID_REGION in np.arange(0,len(nuts1)):
            # for ID_REGION in [7, 36, 48, 49, 50, 92, 95, 97, 99, 100]: # the interesting countries
                
                
                # Determine the region name
                region_name = nuts0.iloc[ID_REGION]['Study Zone']
                print('      : ('+str(ID_REGION+1)+'/112) '+region_name+'!')
            
                if region_name[-4:] != '_OFF':
                    
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
                   
                    
                  
                            
                
                    #%%
                    # =============================================================================
                    # Regional mean for saving data
                    # =============================================================================
        
                    # Weighted mean
                    out_sel_of = out_sel.weighted(weights_pop)
                    PWT.append(out_sel_of.mean(("lat","lon")).t2m.values)
                                        
                    # Just a list of names
                    REGION_NAME.append(region_name)
            
            
            # out of the region loop we create new arrays with the info
            ds_save = xr.Dataset()
            ds_save['PWT']  = xr.DataArray(PWT, coords=[REGION_NAME, ds.time], dims=["region", "time"])
            
            #%%                
            # =============================================================================
            # Setting units & saving
            # =============================================================================
            
            
            # Setting the general dataset attributes
            ds_save.attrs.update(
                author = 'Laurens Stoop UU/KNMI/TenneT',
                units = '[a.u.]',
                created = datetime.datetime.today().strftime('%d-%m-%Y'),
                map_area = 'Europe',
                region_definition = 'ENTSO-E StudyZones at national level aggregated',
                data_source = 'Population weighted temperarute for each ENTSO-E zone, contains modified Copernicus Climate Change Service information [28-02-2022]'
                )
            
            
            # Saving the file
            ds_save.to_netcdf(file_save, encoding={'time':{'units':'days since 1900-01-01'}})
            
