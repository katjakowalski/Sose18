import time
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("Starting process, time: " + starttime)
print("--------------------------------------------------------")
print("")
########################################################################
from osgeo import gdal, ogr, osr
import pandas as pd
import os
import numpy as np
import geopandas as gpd
import math
import random as rd
from shapely import wkt
########################################################################

root_folder = '/Users/Katja/Documents/Studium/Sose18/week09/Assignment07_data/'

# tmp = gpd.GeoDataFrame.from_file(root_folder + '/Points.shp')
# samples_lambert = tmp.to_crs({'init':'EPSG:3035'})
# samples_lambert.to_file(root_folder + 'samples_lambert.shp')
#
# tmp = gpd.GeoDataFrame.from_file(root_folder + '/Old_Growth.shp')
# ogr_lambert = tmp.to_crs({'init':'EPSG:3035'})
# ogr_lambert.to_file(root_folder + 'ogr_lambert.shp')
#
# tmp = gpd.GeoDataFrame.from_file(root_folder + '/PrivateLands.shp')
# pl_lambert = tmp.to_crs({'init':'EPSG:3035'})
# pl_lambert.to_file(root_folder + 'pl_lambert.shp')
#
# filename = root_folder + '/Elevation.tif'
# input_raster = gdal.Open(filename)
# output_raster = root_folder + 'elevation_lambert.tif'
# gdal.Warp(output_raster,input_raster,dstSRS='EPSG:3035')

driver = ogr.GetDriverByName("ESRI Shapefile")
PL = driver.Open(root_folder + 'PrivateLands.shp',1)
OGF = driver.Open(root_folder + 'Old_Growth.shp',1)
pts = driver.Open(root_folder + 'Points.shp',1)

PL_lyr = PL.GetLayer()
OGF_lyr = OGF.GetLayer()
pts_lyr = pts.GetLayer()

elev = gdal.Open('/Users/Katja/Documents/Studium/Sose18/week09/Assignment07_data/elevation_lambert.tif')
road = gdal.Open('/Users/Katja/Documents/Studium/Sose18/week09/Assignment07_data/DistToRoad.tif')



pr_ras = elev.GetProjection()               # get projection from raster

source_SR = pts_lyr.GetSpatialRef()         # get spatial reference from sample layer
target_SR = osr.SpatialReference()          # create empty spatial reference
target_SR.ImportFromWkt(pr_ras)             # get spatial reference from projection of raster
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)     # transformation rule for coordinates from samples to elevation raster


feat = pts_lyr.GetNextFeature()
df = list()
while feat:
    # ELEVATION
    ide = feat.GetField('ID')                   # get ID
    coord = feat.GetGeometryRef()
    coord_cl = coord.Clone()
    coord_cl.Transform(coordTrans)          # apply coordinate transformation
    pr_elev = elev.GetProjection()          # get projection and transformation to calculate absolute raster coordinates
    gt_elev = elev.GetGeoTransform()
    x, y = coord_cl.GetX(), coord_cl.GetY()
    px_elev = int((x - gt_elev[0]) / gt_elev[1])
    py_elev = int((y - gt_elev[3]) / gt_elev[5])
    #readraster
    #coord_cl =

    # ROAD
    pr_road = road.GetProjection()
    gt_road = road.GetGeoTransform()

    #if PL_geom.Contains(spnt):
     #   PL = 1
    #else: PL = 0
    df.append([ide, x,y])
    feat = pts_lyr.GetNextFeature()
pts_lyr.ResetReading()
#print(df)

########################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)