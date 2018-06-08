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

root_folder = "/Users/Katja/Documents/Studium/Sose18/week08/Assignment06 - data/"

ras1 = gdal.Open("/Users/Katja/Documents/Studium/Sose18/week08/Assignment06_data/Tile_x17999_y20999_1000x1000.tif")
ras2 = gdal.Open("/Users/Katja/Documents/Studium/Sose18/week08/Assignment06_data/Tile_x19999_y32999_1000x1000.tif")
ras3 = gdal.Open("/Users/Katja/Documents/Studium/Sose18/week08/Assignment06_data/Tile_x26999_y12999_1000x1000.tif")

# print(ras1.GetGeoTransform())
# print(ras2.GetGeoTransform())
# print(ras3.GetGeoTransform())

arr1 = np.array(ras1.ReadAsArray())
arr2 = np.array(ras2.ReadAsArray())
arr3 = np.array(ras3.ReadAsArray())

#print(arr1.shape[0])
#print(arr2.shape)
#print(arr3.shape)

arr_list = list((arr1, arr2, arr3))


def make_slices(data, rows, cols):
    """Return a list of slices given a window size.
    data     - two-dimensional array to get slices from
    win_size - tuple of (rows, columns) for the moving window
    """
    yrange = data.shape[0] - rows + 1
    xrange = data.shape[1] - cols + 1
    slices = []
    counter = 0
    for i in range(xrange):
        counter += 1
        for j in range(yrange):
            data_st = data[i:rows+i, j:cols+j]
            slices.append(data_st)
    slices_final = np.asarray(slices)
    print('Slices:', counter)
    return(slices_final)

# #ras 1
slices1_11 = make_slices(arr1, 11, 11)
#slices1_21 = make_slices(arr1, 21, 21)
#slices1_31 = make_slices(arr1, 31, 31)
print(slices1_11.shape)
#print(slices1_11.shape)

# # stack1_11 = slice_list.append(np.dstack(slices1_11))
# # stack1_21 = slice_list.append(np.dstack(slices1_21))
# # stack1_31 = slice_list.append(np.dstack(slices1_31))
#
# #ras 2
#slices2_11 = make_slices(arr2, 11,11)
#slices2_21 = make_slices(arr2, 21,21)
#slices2_31 = make_slices(arr2, 31,31)
#
# # stack2_11 = slice_list.append(np.dstack(slices2_11))
# # stack2_21 = slice_list.append(np.dstack(slices2_21))
# # stack2_31 = slice_list.append(np.dstack(slices2_31))
#
# #ras 3
#slices3_11 = make_slices(arr3, 11,11)
#slices3_21 = make_slices(arr3, 21,21)
#slices3_31 = make_slices(arr3, 31,31)
#
# # stack3_11 = slice_list.append(np.dstack(slices3_11))
# # stack3_21 = slice_list.append(np.dstack(slices3_21))
# # stack3_31 = slice_list.append(np.dstack(slices3_31))
#
# #print(slices1_11[4].shape)

def shdi(data):
    results = []
    #counter +=1
    cat_list =[1,2,3,5,11,13,17,18,19]
    unique, counts = np.unique(data, return_counts=True)
    dict1 = dict(zip(unique, counts))
    p_dict = {}
    for cat in cat_list:                                        # loop through every category in the list
        if cat in dict1:                                        # if this category is represented in the slice
            p_dict.update({cat: dict1[cat]})                        # keep only the counts and keys that are in the list and the slice
    cat_sum = sum(p_dict.values())                               # get sum of all pixels containing one of the category values
    for cat in cat_list:
        if cat in dict1:
            prop = (p_dict[cat]/cat_sum)
            shdi = (prop * math.log10(prop))
            results.append(shdi)
    shdi_fin = sum(results) * (-1)
    #shdi_arr = np.asarray(shdi_fin)
    #print(shdi_list)
    return(shdi_fin)


arr_test = np.apply_along_axis(shdi, axis=2, arr= slices1_11)
print(arr_test)
print(len(arr_test))

#print(shdi(slices1_11))

#out_data = np.ones((1000,1000)) * -99
#out_data[5:995, 5:995] = np.asarray(slices1_11)


# # Save raster - code from class
# # 0. Formulate an outputName
# ras_B12 = root_folder + "dem_slope.tif"
# # 1. Create a driver with which we write the output
# drvR = gdal.GetDriverByName('GTiff')
# # 2. Create the file (here: allthough exactly the same, we go through the syntax)
# pr1 = ras1.GetProjection()
# pr2 = ras2.GetProjection()
# pr3 = ras3.GetProjection()
# outDS = drvR.Create(ras_B12, 599, 1240, 1)
# outDS.SetProjection(pr1)
# outDS.SetGeoTransform(gt_dem) # dont need this ?
# # 3. Write the array into the newly generated file
# outDS.GetRasterBand(1).WriteArray(arr_B12, 0, 0)#(array, offset_x, offset_y)


########################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)


