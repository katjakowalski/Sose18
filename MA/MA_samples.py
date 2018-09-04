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
import shapely
import fiona
import struct
from pyproj import Proj, transform
import geopandas as gpd
#####################################################################################

root_folder = "/Users/Katja/Documents/Studium/MA/Sampling_data/"
os.chdir("/Users/Katja/Documents/Studium/MA/Sampling_data/")

undist_forest = gdal.Open("/Users/Katja/Documents/Studium/MA/Sampling_data/germany_landcover_2015_g1416lc3_dbf_undisturbed_erode3x3_mmu11.bsq")
lc_forest = gdal.Open("/Users/Katja/Documents/Studium/MA/Sampling_data/germany_landcover_2015_g1416lc3.tif")

gt_for = undist_forest.GetGeoTransform()


# open shapefile
driver = ogr.GetDriverByName("ESRI Shapefile")
#station_shp = driver.Open(root_folder + '/sample_pts/stat_dwd_3035.shp', 1)
#station = station_shp.GetLayer()

germany_shp = driver.Open(root_folder +'/germany.shp', 1)
germany = germany_shp.GetLayer()

b_shp = driver.Open(root_folder + '/sample_pts/dwd_1km.shp', 1)
b_lyr = b_shp.GetLayer()


b_feat = b_lyr.GetNextFeature()
while b_feat:
    geom = b_feat.GetGeometryRef()
    x_min_b, x_max_b, y_min_b, y_max_b = b_feat.geometry().GetEnvelope()    # get extent of sampling area
    print(x_min_b, x_max_b, y_min_b, y_max_b)
    # for x in tile_list:
    #     x_min_t, x_max_t, y_min_t, y_max_t =                                # get extent of tile, which then should be band 1 in stack
    #     # get extent somehow and store in variables
    #     if x_min_b >= x_min_t and x_max_b <= x_max_t and y_min_b >= y_min_t and y_max_b <= y_max_t:             # check if area contained in file
    #         x1 = rd.uniform(x_min_b, x_max_b)
    #         y1 = rd.uniform(y_min_b, y_max_b)
    #         point = ogr.Geometry(ogr.wkbPoint)                              # create empty geometry and then add point geometry from coordinates
    #         point.AddPoint(x1, y1)
    #         if point.within(geom):                                          # check if point falls within circular area
    #             px_ras = int((x - gt_ras[0]) / gt_ras[1])                   # calculate absolute raster coordinates
    #             py_ras = int((y - gt_ras[3]) / gt_ras[5])
    b_feat = b_lyr.GetNextFeature()








        #####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")