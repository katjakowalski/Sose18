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
# TASK 1
    # get overlap of (1) four raster files and (2) vegetation raster > array slicing > create mask and sample from there (??)
    # stratified random sample (100 pts. in 5 strata > 500 pts total)

    # rd.randint()

###### FUNCTIONS ###########

def corner_coordinates(file_list):
    '''returns corner coordinates of all raster input files'''
    UL_x_list = []
    UL_y_list = []
    LR_x_list = []
    LR_y_list = []
    for i in file_list:
        LS = gdal.Open(i)
        gt = LS.GetGeoTransform()
        UL_x, UL_y = gt[0], gt[3]
        LR_x = UL_x + gt[1] * LS.RasterXSize
        LR_y = UL_y + gt[5] * LS.RasterYSize
        UL_x_list.append(UL_x)
        UL_y_list.append(UL_y)
        LR_x_list.append(LR_x)
        LR_y_list.append(LR_y)
        LS_list.append(LS)
        #print(os.path.basename(i), 'Upper Left X:',UL_x, 'Lower Right X:', LR_x)
    x_min = max(UL_x_list)
    x_max = min(LR_x_list)
    y_min = max(LR_y_list)
    y_max = min(UL_y_list)
    return(x_min, x_max, y_min, y_max)


######################################################
# Aim: make sure that raster files have the same extent
## search for all files in subfolders of data
root_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task01_data/"
LS_list = list()            # list all subdirectories with file path and name of subfolders
file_list = list()
for root, dirs, files in os.walk(root_folder, topdown=False):
    for name in files:
        file_list.append(os.path.join(root ,name))

# create 4 lists with all raster files of respective tile
tile_1 = [i for i in file_list if '38999' in i]
tile_2 = [i for i in file_list if '39999' in i]
tile_3 = [i for i in file_list if '40999' in i]
tile_4 = [i for i in file_list if '41999' in i]

tile_1 = [i for i in tile_1 if '.hdr' not in i]
tile_2 = [i for i in tile_2 if '.hdr' not in i]
tile_3 = [i for i in tile_3 if '.hdr' not in i]
tile_4 = [i for i in tile_4 if '.hdr' not in i]


# get corner coordinates = sample boundary
x_min, x_max, y_min, y_max = corner_coordinates(tile_1)
print(x_min, x_max, y_min, y_max)

# coordinate transformation
ras_veg = gdal.Open(root_folder + '/2000_VCF/20S_070W.tif')
pr_veg = ras_veg.GetProjection()               # get projection from Veg. raster
#print(pr_veg)
target_SR = osr.SpatialReference()          # create empty spatial reference
target_SR.ImportFromWkt(pr_veg)             # get spatial reference from projection of raster

# coordinate transformation Landsat/Sentinel data <> Vegetation data
ras_LS = gdal.Open(root_folder + '/2015_L8_doy015/Tile_x18999_y38999_1000x1000_2014-2015_CHACO_PBC_multiYear_Imagery.bsq')
pr_LS = ras_LS.GetProjection()               # get projection from Veg. raster
#print(pr_LS)
source_SR = osr.SpatialReference()          # create empty spatial reference
source_SR.ImportFromWkt(pr_LS)             # get spatial reference from projection of raster
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)     # transformation rule for coordinates from samples to elevation raster


# create random samples in interval (float) and add ID and coordinates to dataframe
count_list1 = []
count_list2 = []
count_list3 = []
count_list4 = []
count_list5 = []
df = pd.DataFrame(columns=['ID', 'X', 'Y'])                         # set up pandas dataframe to store data

while len(count_list1) < 100 and len(count_list2) < 100 and len(count_list3) < 100 and len(count_list4) <100 and len(count_list5)<100:
    x1 = rd.uniform(x_min, x_max)                                   # random value in x range
    y1 = rd.uniform(y_min, y_max)                                   # random value in y range
    ras = gdal.Open(root_folder + '/2000_VCF/20S_070W.tif')
    rb_ras = ras.GetRasterBand(1)
    point = ogr.Geometry(ogr.wkbPoint)                              # create point geometry from coordinates
    point.AddPoint(x1, y1)
    #print(point)
    #coord = point.GetGeometryRef()
    coord_cl = point.Clone()                                        # clone sample geometry
    coord_cl.Transform(coordTrans)                                  # apply coordinate transformation
    x, y = coord_cl.GetX(), coord_cl.GetY()                         # get x and y coordinates of transformed sample point
    print(x,y)
    struc_ras = rb_ras.ReadRaster(x, y, 1, 1)
    if struc_ras is None:
        val = struc_ras
    else:
        val_ras = struct.unpack('H', struc_ras)
        val = val_ras[0]
    print(val)
    # if val == None:
    #     print("No Data")
    # if 0 <= val <= 20:
    #     count1 = len(count_list1)
    #     df.loc[len(df) + 1] = [count1, x, y]
    #     count_list1.append(1)
    # else: print('coordinate not in stratum 1 ')
    # if 21 <= val <= 40:
    #     count2 = len(count_list2)
    #     df.loc[len(df) + 1] = [count2, x, y]
    #     count_list2.append(1)
    # if 41 <= val <= 60:
    #     count3 = len(count_list3)
    #     df.loc[len(df) + 1] = [count3, x, y]
    #     count_list3.append(1)
    # if 61 <= val <= 80:
    #     count4 = len(count_list4)
    #     df.loc[len(df) + 1] = [count4, x, y]
    #     count_list4.append(1)
    # if 81 <= val <= 100:
    #     count5 = len(count_list5)
    #     df.loc[len(df) + 1] = [count5, x, y]
    #     count_list1.append(1)
print(df)

#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")