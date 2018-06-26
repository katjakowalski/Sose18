import time
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("Starting process, time: " + starttime)
print("--------------------------------------------------------")
print("")
########################################################################
from osgeo import gdal, ogr, osr
import struct
import pandas as pd
import os
import glob
import numpy as np
import geopandas as gpd
import math
import random as rd
from shapely import wkt

########################################################################

root_folder = "/Users/Katja/Documents/Studium/Sose18/week11/Assignment09_data/"
file_list = glob.glob(os.path.join(root_folder, '*.tif'))


def array_overlap(file_list):
    UL_x_list = list()
    UL_y_list = list()
    LR_x_list = list()
    LR_y_list = list()
    LS_list = list()
    arr_list = list()
    for i in file_list:
        LS = gdal.Open(i)
        gt = LS.GetGeoTransform()
        UL_x, UL_y = gt[0], gt[3]
        LR_x = UL_x + gt[1]* LS.RasterXSize
        LR_y = UL_y + gt[5]* LS.RasterYSize
        UL_x_list.append(UL_x)
        UL_y_list.append(UL_y)
        LR_x_list.append(LR_x)
        LR_y_list.append(LR_y)
        LS_list.append(LS)
        print(os.path.basename(i), 'Upper Left X:',UL_x, 'Upper Left Y:', UL_y, 'Lower Right X:', LR_x, 'Lower Right Y:', LR_y)

    for i in file_list:
        LS2 = gdal.Open(i,gdal.GA_ReadOnly)
        x_range = int((min(LR_x_list) - max(UL_x_list)) // gt[1])    # get minimal x and y range of all datasets
        y_range = int((min(UL_y_list) - max(LR_y_list)) // gt[1])
        gt_LS = LS2.GetGeoTransform()                           # get GT of current dataset
        inv_ft = gdal.InvGeoTransform(gt_LS)                    # invert GT of current dataset
        UL_x2, UL_y2 = gt_LS[0], gt_LS[3]
        offsets = gdal.ApplyGeoTransform(inv_ft, UL_x2, UL_y2)  # define offsets, use current UL_x and UL_y ???
        xoff, yoff = map(int, offsets)
        arr_list.append(LS2.ReadAsArray(xoff, yoff, x_range, y_range))
        print('UL X:', max(UL_x_list), 'UL Y:', min(UL_y_list))
        print('LR X:', min(LR_x_list), 'LR Y:', max(LR_y_list))
        print('X range', x_range)  # no of columns in x direction
        print('Y range', y_range)  # no of rows in y direction
    return(arr_list)

arr_list = array_overlap(file_list)

print(arr_list[0].shape)

arr_class = arr_list[0]*0
print(arr_class.shape)

driver = ogr.GetDriverByName("ESRI Shapefile")
pts = driver.Open(root_folder + 'RandomPoints.shp',1)
pts_lyr = pts.GetLayer()


ras1 = gdal.Open('/Users/Katja/Documents/Studium/Sose18/week11/Assignment09_data/LE07_L1TP_117056_20040211_20170122_01_T1_sr_evi.tif')
pr_ras1 = ras1.GetProjection()               # get projection from raster
source_SR = pts_lyr.GetSpatialRef()         # get spatial reference from sample layer
target_SR = osr.SpatialReference()          # create empty spatial reference
target_SR.ImportFromWkt(pr_ras1)             # get spatial reference from projection of raster
coordTrans_ras = osr.CoordinateTransformation(source_SR, target_SR)     # transformation rule for coordinates from samples to elevation raster


feat = pts_lyr.GetNextFeature()
df = list()

out_array = np.zeros((pts_lyr.GetFeatureCount(),4))
print(arr_tr)

while feat:
    #ide = feat.GetField('Id')                   # get ID
    pt_class = feat.GetField('Class')
    coord = feat.GetGeometryRef()
    coord_cl = coord.Clone()
    coord_cl.Transform(coordTrans_ras)          # apply coordinate transformation
    #gt_ras = ras1.GetGeoTransform()             # get projection and transformation to calculate absolute raster coordinates
    x, y = coord_cl.GetX(), coord_cl.GetY()
    for i in file_list:
        ras = gdal.Open(i)
        gt_ras = ras.GetGeoTransform()
        px_ras = int((x - gt_ras[0]) / gt_ras[1])
        py_ras = int((y - gt_ras[3]) / gt_ras[5])
        rb_ras = ras.GetRasterBand(1)
        #print(rb_ras.DataType)
        struc_ras = rb_ras.ReadRaster(px_ras, py_ras, 1, 1)
        #print(struc_ras)fwferfer
        if struc_ras is None:
            value_ras = struc_ras
        else:
            val_ras = struct.unpack('H', struc_ras)
            value_ras = val_ras[0]

            for i in range(len(file_list)):
                out_array[:, i] = ras[i].ravel()  # ravel() reduces the dimensions of an array
            out_array
        #print(value_ras)
    feat = pts_lyr.GetNextFeature()
pts_lyr.ResetReading()


########################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)