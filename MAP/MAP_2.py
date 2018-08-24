import time

starttime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
print("Starting process, date and time: " + starttime)
print("--------------------------------------------------------")
print("")

#####################################################################################
# import additional packages
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import math
from joblib import Parallel, delayed
import multiprocessing
import os
import glob
import Package
from Package import rastertools
import random as rd
import struct
from pyproj import Proj, transform
import geopandas as gpd
from functools import reduce
#####################################################################################

root_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task02_data/"

driver = ogr.GetDriverByName("ESRI Shapefile")
country_shp = driver.Open(root_folder + '/ZonalShape_Countries_Europe_NUTS1_multipart.shp', 1)
dam_shp = driver.Open(root_folder + '/GRanD_dams_v1_1_Europe-sub.shp',1)
road_shp = driver.Open(root_folder + '/gRoads-v1-Europe-sub.shp',1)

countries_lyr = country_shp.GetLayer()
roads_lyr = road_shp.GetLayer()
dams_lyr = dam_shp.GetLayer()

# coordinate transformation
source_SR = dams_lyr.GetSpatialRef()
target_SR = countries_lyr.GetSpatialRef()
coordTrans= osr.CoordinateTransformation(source_SR, target_SR)

# loop through dams
dam_feature = dams_lyr.GetNextFeature()
df = []
while dam_feature:
    coord = dam_feature.GetGeometryRef()
    coord_cl = coord.Clone()
    coord_cl.Transform(coordTrans)                  # transform coordinate to crs of country layer
    countries_lyr.SetSpatialFilter(coord_cl)            # set spatial filter to select country

    for country in countries_lyr:                       # extract country for dam
        country_name = country.GetField('NAME_0')
    countries = countries_lyr.SetAttributeFilter("NAME_0 = country_name")

    df.append([dam_feature.GetField('DAM_NAME'),        # transfer to nested list
               dam_feature.GetField('YEAR'),
               dam_feature.GetField('AREA_SKM'),
               dam_feature.GetField('DEPTH_M'),
               dam_feature.GetField('ELEV_MASL'),
               dam_feature.GetField('CATCH_SKM'),
               country_name])

    countries_lyr.SetSpatialFilter(None)                # remove spatial filter
    dam_feature = dams_lyr.GetNextFeature()
dams_lyr.ResetReading()

# convert list to pandas dataframe
field_names = list(('name', 'year',  'area_skm', 'depth_m', 'elev_masl', 'catch_skm', 'country'))
df_pandas = pd.DataFrame.from_records(df, columns = field_names)

# group dataframe and extract information
## 1. number of damns per country
nr_dams = df_pandas.groupby(['country'], as_index=False)['country'].agg(['count'])

## 2. year of establishment of oldest dam
yr_old = df_pandas.groupby(['country'], as_index=False)['year'].min()

## 3. name of oldest dam
idx = df_pandas.groupby(['country'])['year'].transform(max) == df_pandas['year']
old_df = df_pandas[idx]
name_old = old_df.drop(['year','area_skm', 'depth_m', 'elev_masl', 'catch_skm'], axis=1)

## 4. year of establishment of youngest dam
yr_young = df_pandas.groupby(['country'],as_index=False)['year'].max()

## 5. name of youngest dam
idx = df_pandas.groupby(['country'])['year'].transform(min) == df_pandas['year']
young_df = df_pandas[idx]
name_young = young_df.drop(['year','area_skm', 'depth_m', 'elev_masl', 'catch_skm'], axis=1)

## 6. average size of reservoir in km2
av_reserv_km2 = df_pandas.groupby(['country'], as_index=False)['area_skm'].mean()

## 7. maximum size of reservoir in km2
max_reserv_km2 = df_pandas.groupby(['country'], as_index=False)['area_skm'].max()

## 8. name of dam with largest reservoir
idx = df_pandas.groupby(['country'])['area_skm'].transform(max) == df_pandas['area_skm']
area_df = df_pandas[idx]
Name_max_reserv = area_df.drop(['year', 'depth_m', 'elev_masl', 'catch_skm', 'area_skm'], axis=1)

## 9. average depth of reservoirs in m
av_depth_reserv_m = df_pandas.groupby(['country'], as_index=False)['depth_m'].mean()

## 10. maximum depth of reservoirs in m
max_depth_reserv_m = df_pandas.groupby(['country'], as_index=False)['depth_m'].max()

## 11. name of dam with deepest reservoir
idx = df_pandas.groupby(['country'])['depth_m'].transform(max) == df_pandas['depth_m']
df1 = df_pandas[idx]
name_max_depth = df1.drop(['year', 'area_skm', 'elev_masl', 'catch_skm', 'depth_m'], axis=1)

## 12. largest catchment in km2
max_catch_km2 = df_pandas.groupby(['country'], as_index=False)['catch_skm'].max()

## 13. name of dam with largest catchment
idx = df_pandas.groupby(['country'])['catch_skm'].transform(max) == df_pandas['catch_skm']
df1 = df_pandas[idx]
Name_max_catch = df1.drop(['year', 'area_skm', 'elev_masl', 'depth_m', 'catch_skm'], axis=1)

# create list of dataframes and merge all to final dataframe
df_fin = [nr_dams,yr_old, name_old, yr_young, name_young, av_reserv_km2, max_reserv_km2, Name_max_reserv, av_depth_reserv_m,
          max_depth_reserv_m, name_max_depth, max_catch_km2, Name_max_catch]
df_final = reduce(lambda left,right: pd.merge(left,right,on='country'), df_fin)

# rename columns
df_final.columns = ['country','nr_dams','yr_old','name_old','yr_young','name_young',
                    'av_reserv_km2','max_reserv_km2','Name_max_depth','av_depth_reserv_m',
                    'max_depth_reserv_m','Name_max_reserv','max_catch_km2','Name_max_catch' ]

# save csv file
df_final.to_csv(path_or_buf= 'Map2.csv', index=False)





### ROADS


#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")