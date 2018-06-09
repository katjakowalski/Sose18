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


ras1 = gdal.Open("/Users/Katja/Documents/Studium/Sose18/week08/Assignment06_data/Tile_x17999_y20999_1000x1000.tif")
ras2 = gdal.Open("/Users/Katja/Documents/Studium/Sose18/week08/Assignment06_data/Tile_x19999_y32999_1000x1000.tif")
ras3 = gdal.Open("/Users/Katja/Documents/Studium/Sose18/week08/Assignment06_data/Tile_x26999_y12999_1000x1000.tif")

arr1 = np.array(ras1.ReadAsArray())
arr2 = np.array(ras2.ReadAsArray())
arr3 = np.array(ras3.ReadAsArray())

def make_slices(data, win_x, win_y):  # e.g. 11,11 window size
    slices = []
    counter = 0
    range1 = (data.shape[0] - win_x) + 1
    range2 = (data.shape[1] - win_y) + 1
    for i in range(win_x):
        counter += 1
        for j in range(win_y):
            data_st = data[i:range1+i, j:range2+j]
            slices.append(data_st)
    slices_final = np.asarray(slices)                           # list to array
    slices_stack = np.ma.dstack(slices_final)                   # stack slices
    print('Slices:', counter)
    return(slices_stack)


def shdi(data):
    results = []
    #counter +=1
    cat_list =[1,2,3,5,11,13,17,18,19]
    # get counts of all categories
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


slices1_11 = make_slices(arr1, 11, 11)
slices1_21 = make_slices(arr1, 21, 21)
slices1_31 = make_slices(arr1, 31, 31)

slices2_11 = make_slices(arr2, 11, 11)
slices2_21 = make_slices(arr2, 21, 21)
slices2_31 = make_slices(arr2, 31, 31)

slices3_11 = make_slices(arr3, 11, 11)
slices3_21 = make_slices(arr3, 21, 21)
slices3_31 = make_slices(arr3, 31, 31)

# apply shdi function with different window sizes
## array 1:
rows = ras1.RasterXSize
cols = ras1.RasterYSize

outdata = np.ones((rows,cols)) * -99
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices1_11)
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices1_21)
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices1_31)

## array 2:
rows = ras2.RasterXSize
cols = ras2.RasterYSize
outdata = np.ones((rows,cols)) * -99
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices2_11)
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices2_21)
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices2_31)

## array 3:
rows = ras3.RasterXSize
cols = ras3.RasterYSize
outdata = np.ones((rows,cols)) * -99
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices3_11)
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices3_21)
outdata[5:-5, 5:-5] = np.apply_along_axis(shdi, 2, slices3_31)

# # Save raster - code from class
# # 0. Formulate an outputName
out_ras = "/Users/Katja/Documents/Studium/Sose18/week08/Assignment06_data/test.tif"
# # 1. Create a driver with which we write the output
drvR = gdal.GetDriverByName('GTiff')

# # 2. Create the file (here: allthough exactly the same, we go through the syntax)
pr1 = ras1.GetProjection()
pr2 = ras2.GetProjection()
pr3 = ras3.GetProjection()
gt1 = ras1.GetGeoTransform()
gt2 = ras2.GetGeoTransform()
gt3 = ras3.GetGeoTransform()

outDS = drvR.Create(out_ras, 1000, 1000, 1, gdal.GDT_Float32)
outDS.SetProjection(pr1)
outDS.SetGeoTransform(gt)
outDS.GetRasterBand(1).WriteArray(outdata, 0, 0)            # 3. Write the array into the newly generated file


########################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)