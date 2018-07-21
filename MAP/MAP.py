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

# coordinate transformation
ras_veg = gdal.Open(root_folder + '/2000_VCF/20S_070W.tif')
ras = ras_veg.GetRasterBand(1)
pr_veg = ras_veg.GetProjection()                                    # get projection from Veg. raster
target_SR = osr.SpatialReference()                                  # create empty spatial reference
target_SR.ImportFromWkt(pr_veg)                                     # get spatial reference from projection of raster

# coordinate transformation Landsat/Sentinel data <> Vegetation data
ras_LS = gdal.Open(root_folder + '/2015_L8_doy015/Tile_x18999_y38999_1000x1000_2014-2015_CHACO_PBC_multiYear_Imagery.bsq')
pr_LS = ras_LS.GetProjection()                                      # get projection from Veg. raster
source_SR = osr.SpatialReference()                                  # create empty spatial reference
source_SR.ImportFromWkt(pr_LS)                                      # get spatial reference from projection of raster
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)     # transformation rule
gt_ras = ras_veg.GetGeoTransform()                                  # get information from vegetation raster


count_list1 = []
count_list2 = []
count_list3 = []
count_list4 = []
count_list5 = []
count_all = []
dat_list = []
df = pd.DataFrame(columns=['ID', 'X', 'Y'])                         # set up pandas dataframe to store data
point_id = 0
while len(count_list1) < 5 or len(count_list2) < 5 or len(count_list3) < 5 or len(count_list4) < 5 or len(count_list5) < 5:
    x1 = rd.uniform(x_min, x_max)                                   # sample random value in x range
    y1 = rd.uniform(y_min, y_max)                                   # sample random value in y range
    point = ogr.Geometry(ogr.wkbPoint)                              # create empty geometry and then add point geometry from coordinates
    point.AddPoint(x1, y1)
    point_id += 1
    #print('sample: ', point)
    for i in tile_list:                                             # loop through all tiles
        tile = gdal.Open(i)
        #print('bands: ', tile.RasterCount)
        gt_tile = tile.GetGeoTransform()                            # get information from tile
        px_tile = int((x1 - gt_tile[0]) / gt_tile[1])               # calculate absolute raster coordinates of sample
        py_tile = int((y1 - gt_tile[3]) / gt_tile[5])
        if px_tile < 1000 and px_tile >= 0 and py_tile < 1000 and py_tile >= 0:
            #print(gt_tile)
            #print(px_tile, py_tile)
            data = tile.ReadAsArray()                               # get array from raster
            if tile.RasterCount == 1:                               # extract values from raster depending on number of bands in raster
                val_band = data[py_tile, px_tile]                   # extract raster value from single band
                #print('point in tile', i)
                dat_list.append([point_id, os.path.basename(os.path.normpath(i)),1, val_band])
            else:
                for x in range(tile.RasterCount):                   # extract raster value from each band
                    val_bands = data[x,py_tile, px_tile]
                    dat_list.append([point_id, os.path.basename(os.path.normpath(i)), x, val_bands])
                    #print('rasterbands:',x ,'value: ', val_bands)

    # extract values from vegetation raster
    coord_cl = point.Clone()  # clone sample geometry
    coord_cl.Transform(coordTrans)  # apply coordinate transformation
    x, y = coord_cl.GetX(), coord_cl.GetY()  # get x and y coordinates of transformed sample point
    # calculate absolute raster coordinates:
    px_ras = int((x - gt_ras[0]) / gt_ras[1])
    py_ras = int((y - gt_ras[3]) / gt_ras[5])

    # extract information from raster and unpack values
    struc_ras = ras.ReadRaster(px_ras, py_ras, 1, 1)
    if struc_ras is None:
        val_veg = struc_ras
    else:
        val_ras = struct.unpack('b', struc_ras)
        val_veg = val_ras[0]

    if val_veg <= 20 and len(count_list1) < 5:
        df.loc[len(df) + 1] = [point_id, x, y]
        count_list1.append(1)
    elif val_veg <= 40 and len(count_list2) < 5:
        df.loc[len(df) + 1] = [point_id, x, y]
        count_list2.append(1)
    elif val_veg <= 60 and len(count_list3) < 5:
        df.loc[len(df) + 1] = [point_id, x, y]
        count_list3.append(1)
    elif val_veg <= 80 and len(count_list4) < 5:
        df.loc[len(df) + 1] = [point_id, x, y]
        count_list4.append(1)
    elif val_veg <= 100 and len(count_list5) < 5:
        df.loc[len(df) + 1] = [point_id, x, y]
        count_list5.append(1)
    #print('veg.value: ', val_veg)

print(dat_list)
field_names = list(('id', 'image', 'band','val'))
df = pd.DataFrame.from_records(dat_list, columns = field_names)
print(df.head())
#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")