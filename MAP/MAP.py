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
        #print(os.path.basename(i), 'Upper Left X:',UL_x, 'Lower Right X:', LR_x)
    x_min = max(UL_x_list)
    x_max = min(LR_x_list)
    y_min = max(LR_y_list)
    y_max = min(UL_y_list)
    return(x_min, x_max, y_min, y_max)


######################################################

# get all files in subfolders of data
root_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task01_data/"
file_list = []
for root, dirs, files in os.walk(root_folder, topdown=False):
    for name in files:
        file_list.append(os.path.join(root ,name))

# create list with all raster files (tiles)
tile_1 = [i for i in file_list if '38999' in i]
tile_2 = [i for i in file_list if '39999' in i]
tile_3 = [i for i in file_list if '40999' in i]
tile_4 = [i for i in file_list if '41999' in i]
tile_list = tile_1 + tile_2 + tile_3 + tile_4
tile_list = [i for i in tile_list if '.hdr' not in i]

# get corner coordinates = sample boundary
x_min, x_max, y_min, y_max = corner_coordinates(tile_list)
print(x_min, x_max, y_min, y_max)

# coordinate transformation
ras_veg = gdal.Open(root_folder + '/2000_VCF/20S_070W.tif')
pr_veg = ras_veg.GetProjection()                                    # get projection from Veg. raster
target_SR = osr.SpatialReference()                                  # create empty spatial reference
target_SR.ImportFromWkt(pr_veg)                                     # get spatial reference from projection of raster

# coordinate transformation Landsat/Sentinel data <> Vegetation data
ras_LS = gdal.Open(root_folder + '/2015_L8_doy015/Tile_x18999_y38999_1000x1000_2014-2015_CHACO_PBC_multiYear_Imagery.bsq')
pr_LS = ras_LS.GetProjection()                                      # get projection from Veg. raster
source_SR = osr.SpatialReference()                                  # create empty spatial reference
source_SR.ImportFromWkt(pr_LS)                                      # get spatial reference from projection of raster
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)     # transformation rule

# ARRAY SLICING
# pt_max = ogr.Geometry(ogr.wkbPoint)  # create empty geometry and then add point geometry from coordinates
# pt_min = ogr.Geometry(ogr.wkbPoint)  # create empty geometry and then add point geometry from coordinates
# pt_min.AddPoint(x_min, y_min)
# pt_max.AddPoint(x_max, y_max)
#
# c_min = pt_min.Clone()  # clone sample geometry
# c_max = pt_max.Clone()
# c_min.Transform(coordTrans)  # apply coordinate transformation
# c_max.Transform(coordTrans)
# x_min, y_min = c_min.GetX(), c_min.GetY()
# x_max, y_max = c_max.GetX(), c_max.GetY()
# print(x_min, x_max, y_min, y_max)
gt_ras = ras_veg.GetGeoTransform()  # get information from vegetation raster
# cols = int((x_min - x_max) / gt_ras[5])
# rows = int((y_min - y_max) / gt_ras[1])
# print(cols, rows)

inv_gt = gdal.InvGeoTransform(gt_ras)
# offsets_ras = gdal.ApplyGeoTransform(inv_gt, x_min ,y_max )
# xoff1, yoff1 = map(int, offsets_ras)
# veg_data = ras_veg.ReadAsArray(xoff1, yoff1, cols, rows)
# print(veg_data)

veg_data = ras_veg.ReadAsArray()
print('read')

# create random samples in interval (float) and add ID and coordinates to dataframe
count_list1 = []
count_list2 = []
count_list3 = []
count_list4 = []
count_list5 = []
count_all = []
df = pd.DataFrame(columns=['ID', 'X', 'Y'])                         # set up pandas dataframe to store data

while len(count_list1) < 1 or len(count_list2) < 1 or len(count_list3) < 1 or len(count_list4) < 1: #or len(count_list5) < 100:
    x1 = rd.uniform(x_min, x_max)                                   # sample random value in x range
    y1 = rd.uniform(y_min, y_max)                                   # sample random value in y range
    point = ogr.Geometry(ogr.wkbPoint)                              # create empty geometry and then add point geometry from coordinates
    point.AddPoint(x1, y1)
    #print('sample: ', point)
    count = []                                                      #### counter for naming of columns in dataframe???
    for i in tile_list:                                             # loop through all tiles
        tile = gdal.Open(i)
        #print('bands: ', tile.RasterCount)
        gt_tile = tile.GetGeoTransform()                            # get information from tile
        px_tile = int((x1 - gt_tile[0]) / gt_tile[1])               # calculate absolute raster coordinates of sample
        py_tile = int((y1 - gt_tile[3]) / gt_tile[5])
        if px_tile <= 1000 and px_tile > 0 and py_tile <= 1000 and py_tile > 0:
            #print(gt_tile)
            print(px_tile, py_tile)
            data = tile.ReadAsArray()                               # get array from raster
            if tile.RasterCount == 1:                               # extract values from raster depending on number of bands in raster
                val_band = data[py_tile, px_tile]                   # extract raster value from single band
                print('point in tile', i)
            else:
                for i in range(tile.RasterCount):                   # extract raster value from each band
                    val_bands = data[i,py_tile, px_tile]
                    print('rasterbands:',i ,'value: ', val_bands)
        else: print('point not in tile:', i)
    #### adding data to df here

    # extract values from vegetation raster
    coord_cl = point.Clone()                                        # clone sample geometry
    coord_cl.Transform(coordTrans)                                  # apply coordinate transformation
    x, y = coord_cl.GetX(), coord_cl.GetY()                         # get x and y coordinates of transformed sample point
    print(x,y)
    px_ras = int((x - gt_ras[0]) / gt_ras[5])                       # calculate absolute raster coordinates:
    py_ras = int((y - gt_ras[3]) / gt_ras[1])
    print(px_ras, py_ras)

    # get the array coordinates > doesnt work
    x_veg, y_veg = map(int, gdal.ApplyGeoTransform(inv_gt, px_ras, py_ras))
    print(x_veg, y_veg)
    val_veg = veg_data[y_veg, x_veg]                              # extract raster value from array
    print(val_veg)

    if val_veg <= 20 and len(count_list1) < 1:
        count1 = len(count_list1)
        df.loc[len(df) + 1] = [count1, x, y]
        count_list1.append(1)
    elif val_veg <= 40 and len(count_list2) < 1:
        count2 = len(count_list2)
        df.loc[len(df) + 1] = [count2, x, y]
        count_list2.append(1)
    elif val_veg <= 60 and len(count_list3) < 1:
        count3 = len(count_list3)
        df.loc[len(df) + 1] = [count3, x, y]
        count_list3.append(1)
    elif val_veg <= 80 and len(count_list4) < 1:
        count4 = len(count_list4)
        df.loc[len(df) + 1] = [count4, x, y]
        count_list4.append(1)
    elif val_veg <= 100 and len(count_list5) < 1:
        count5 = len(count_list5)
        df.loc[len(df) + 1] = [count5, x, y]
        count_list5.append(1)
    print('veg.value: ', val_veg)



#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")