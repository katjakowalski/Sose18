import time

starttime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
print("Starting process, date and time: " + starttime)
print("--------------------------------------------------------")
print("")

#####################################################################################
# import additional packages
from osgeo import gdal, ogr, osr
import pandas as pd
from shapely import wkt
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
from decimal import Decimal
import sys
import os
#####################################################################################
print('hello')
root_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task02_data/"

driver = ogr.GetDriverByName("ESRI Shapefile")
country_shp = driver.Open(root_folder + '/ZonalShape_Countries_Europe_NUTS1_multipart.shp', 1)
dam_shp = driver.Open(root_folder + '/GRanD_dams_v1_1_Europe-sub.shp',1)
road_shp = driver.Open(root_folder + '/gRoads-v1-Europe-sub.shp',0)

countries_lyr = country_shp.GetLayer()
roads_lyr = road_shp.GetLayer()
dams_lyr = dam_shp.GetLayer()

# reproject roads and country shapefiles to epsg 3035 (Lambert Equal Area) to work with spatial resolution in m
driver = ogr.GetDriverByName("ESRI Shapefile")
# tmp = gpd.GeoDataFrame.from_file(root_folder + '/gRoads-v1-Europe-sub.shp')
# roads_3035 = tmp.to_crs({'init':'EPSG:3035'})
# roads_3035.to_file(root_folder + 'roads_3035.shp')
ro = driver.Open(root_folder + '/roads_3035.shp',0)
roads_3035 = ro.GetLayer()

# tmp = gpd.GeoDataFrame.from_file(root_folder + '/ZonalShape_Countries_Europe_NUTS1_multipart.shp')
# countries_3035 = tmp.to_crs({'init':'EPSG:3035'})
# countries_3035.to_file(root_folder + 'countries_3035.shp')
# driver = ogr.GetDriverByName("ESRI Shapefile")
co = driver.Open(root_folder + '/countries_3035.shp',0)
countries_3035 = co.GetLayer()
print('shapefiles loaded')

# coordinate transformation
source_SR = dams_lyr.GetSpatialRef()
target_SR = countries_lyr.GetSpatialRef()
coordTrans= osr.CoordinateTransformation(source_SR, target_SR)

source_SR = countries_lyr.GetSpatialRef()
target_SR = roads_lyr.GetSpatialRef()
coordTrans_roads = osr.CoordinateTransformation(source_SR, target_SR)

# create list with all country names
co_list = set()
for country in countries_lyr:
    co_name = country.GetField('NAME_0')
    co_list.add(co_name)                            # adds only country names which are not in list already
co_list = list(co_list)

print('country list ready')
area_final = []

for i in co_list:                                                   # loop through each country in list
    area_list = []
    counter = 0
    countries_lyr.SetAttributeFilter("NAME_0 = '"+str(i)+"'")       # set attribute filter on respective country
    co_feat = countries_lyr.GetNextFeature()
    while co_feat:                                                  # loop through all features of country i
        area = co_feat.GetField('area_km2')                         # get the area to calculate overall country area
        area_list.append(area)
        co_feat = countries_lyr.GetNextFeature()
    area_final.append([i, round(sum(area_list),2)])
countries_lyr.SetAttributeFilter(None)
print('country area ready')

# working with roads and countries in epsg 3035
length_list = []
nr_list = []
country_feat = countries_3035.GetNextFeature()
while country_feat:
    #counter_c += 1
    #print(counter_c)
    co_geom = country_feat.GetGeometryRef()
    i = country_feat.GetField('NAME_0')
    roads_3035.SetSpatialFilter(co_geom)
    fc = roads_3035.GetFeatureCount()
    nr_list.append([i, fc])
    if fc > 0:
        road_feat = roads_3035.GetNextFeature()
        while road_feat:
            length = road_feat.GetField('LENGTH_KM')
            length_list.append([i,length])
            road_feat = roads_3035.GetNextFeature()
    else: print('no roads in', i)
    #print('country', i)
    roads_3035.SetSpatialFilter(None)
    country_feat = countries_3035.GetNextFeature()

print('while loop roads done')

field_names_nr = list(('country', 'nr_roads'))
df_nr = pd.DataFrame.from_records(nr_list, columns= field_names_nr)
print(df_nr.head)
field_names_len = list(('country', 'length_km'))
df_len = pd.DataFrame.from_records(length_list, columns = field_names_len)

nr_roads = df_nr.groupby(['country'], as_index=False)['country'].sum([]).reset_index()
len_roads = df_len.groupby(['country'], as_index=False)['country'].sum([]).reset_index()

df_roads = nr_roads.merge(len_roads, how='outer', on='country')

df_roads.to_csv(path_or_buf= 'df_roads.csv', index=False)

# loop through dams
dam_feature = dams_lyr.GetNextFeature()
df = []
while dam_feature:
    coord = dam_feature.GetGeometryRef()
    coord_cl = coord.Clone()
    coord_cl.Transform(coordTrans)                      # transform coordinate to crs of country layer
    countries_lyr.SetSpatialFilter(coord_cl)            # set spatial filter to select country

    for country in countries_lyr:                       # extract country for dam
        country_name = country.GetField('NAME_0')

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


########################################################################################################################

field_names = list(('name', 'year',  'area_skm', 'depth_m', 'elev_masl', 'catch_skm', 'country'))
df_pandas = pd.DataFrame.from_records(df, columns = field_names)

# group dataframe and extract information
## 2. area of the country in km2
area_km2 = pd.DataFrame.from_records(area_final, columns= ['country','area_km2'])

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
df_final = reduce(lambda left, right: pd.merge(left, right,on='country'), df_fin)

# rename columns
df_final.columns = ['country','nr_dams','yr_old','name_old','yr_young','name_young',
                    'av_reserv_km2','max_reserv_km2','Name_max_depth','av_depth_reserv_m',
                    'max_depth_reserv_m','Name_max_reserv','max_catch_km2','Name_max_catch' ]

# merge with country area, use outer join to keep all rows (i.e. countries without dams)
df_final = df_final.merge(area_km2, how='outer', on='country')

# some dams where built in the same year, however, here I just select the first in alphabetical order and drop the other(s)
df_final.sort_values(by=['country', 'name_old', 'name_young', 'Name_max_depth', 'Name_max_reserv', 'Name_max_catch'])
df_final = df_final.drop_duplicates(subset=['country'], keep = 'first')

# save csv file
df_final.to_csv(path_or_buf= 'Map2.csv', index=False)

########################################################################################################################

## 2. & 3. mean and maximum distance to road in km
# calculate raster file with distances to roads for entire area
# countries_lyr.SetSpatialFilter(None)
# countries_lyr.SetAttributeFilter(None)
#
# minx, maxx, miny, maxy = countries_3035.GetExtent()
#
# print('max x:', maxx, 'min x:', minx, 'max y:',maxy, 'min y:', miny)
#
# # define output raster col, row, cellsize
# tif_driver = gdal.GetDriverByName('GTiff')
# cellsize = 10
#
# cols = int((maxx - minx) / cellsize)
# rows = int((maxy - miny) / cellsize)
#
# # create raster with roads
# road_ds = tif_driver.Create(root_folder + 'roads.tif', cols, rows)
# road_ds.SetProjection(roads_3035.GetSpatialRef().ExportToWkt())
# road_ds.SetGeoTransform((minx, cellsize, 0, maxy, 0, -cellsize))
# gdal.RasterizeLayer(road_ds, [1], roads_lyr, burn_values=[1], callback=gdal.TermProgress)
#
# # create proximity raster
# prox_ds = tif_driver.Create(root_folder + 'proximity_ras.tif', cols, rows)
# print(prox_ds)
# prox_ds.SetProjection(road_ds.GetProjection())
# prox_ds.SetGeoTransform(road_ds.GetGeoTransform())
# gdal.ComputeProximity(road_ds.GetRasterBand(1), prox_ds.GetRasterBand(1), ['DISTUNITS=GEO'],gdal.TermProgress)
#
# # write 2 raster files to disk
# prox_ds.FlushCache()
# road_ds.FlushCache()
# road_ds = None
# prox_ds = None


#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")