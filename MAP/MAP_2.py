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
#####################################################################################

root_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task02_data/"

driver = ogr.GetDriverByName("ESRI Shapefile")
country_shp = driver.Open(root_folder + '/ZonalShape_Countries_Europe_NUTS1_multipart.shp', 1)
dam_shp = driver.Open(root_folder + '/GRanD_dams_v1_1_Europe-sub.shp',1)
road_shp = driver.Open(root_folder + '/gRoads-v1-Europe-sub.shp',1)

countries_lyr = country_shp.GetLayer()
roads = road_shp.GetLayer()
dams_lyr = dam_shp.GetLayer()

# coordinate transformation
source_SR = dams_lyr.GetSpatialRef()
target_SR = countries_lyr.GetSpatialRef()
coordTrans= osr.CoordinateTransformation(source_SR, target_SR)

# create copy of dam shapefile in memory
# drv = ogr.GetDriverByName( 'Memory' )
# outds = drv.CreateDataSource( '' )
# dams = outds.CopyLayer(dams_lyr,'test2')
# defn = dams.GetLayerDefn()

# create new attribute 'country' in shapefile
#layer_defn = dams.GetLayerDefn()
#field_defn = ogr.FieldDefn('country', ogr.OFTString) # define new field for shapefile
#field_defn.SetWidth(20) # set length of string
#dams.CreateField(field_defn)


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

    df.append([dam_feature.GetField('DAM_NAME'), dam_feature.GetField('YEAR'),
               dam_feature.GetField('AREA_SKM'),dam_feature.GetField('DEPTH_M'), dam_feature.GetField('ELEV_MASL'),
               dam_feature.GetField('CATCH_SKM'), country_name])

    #dams.SetFeature(dam_feature)                    # write country name into new attribute
    #dam_feature.SetField("country", country_name)
    #dams.SetFeature(dam_feature)

    countries_lyr.SetSpatialFilter(None)                # remove spatial filter
    dam_feature = dams_lyr.GetNextFeature()
dams_lyr.ResetReading()


field_names = list(('name', 'year',  'area_skm', 'depth_m', 'elev_masl', 'catch_skm', 'country'))
df_pandas = pd.DataFrame.from_records(df, columns = field_names)

yr_young = df_pandas.groupby(['country'])['year'].max().reset_index()
yr_old = df_pandas.groupby(['country'])['year'].min().reset_index()
#print(yr_young.head)

joined_df = pd.merge(yr_young, yr_old, on='country', how='outer')

print(joined_df.head)

#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")