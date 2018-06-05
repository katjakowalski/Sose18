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
    #arr2 = np.zeros(shape= (121, 1))
    print('Array dimensions:',arr2.shape)
    slices = []
    counter = 0
    #result_array = np.empty((121, 1), dtype= int)
    for i in range(xrange):
        counter += 1
        for j in range(yrange):
            data_st = data[i:rows+i, j:cols+j]
            arr1dim = data_st.flatten()
            slices.append(arr1dim)
            #print(slices)
            #result_array = np.append(result_array, [arr1dim])
            #print(result_array)
            #arr2dim = np.concatenate([arr1dim])
            #sl_array = np.concatenate(arr1, arr2)
    print('Slices:', counter)
    slices_arr = np.asarray(slices)
    return(slices_arr)



# #ras 1
slices1_11 = make_slices(arr1, 11, 11)
slices1_21 = make_slices(arr1, 21, 21)
slices1_31 = make_slices(arr1, 31, 31)
print(slices1_11)

# # stack1_11 = slice_list.append(np.dstack(slices1_11))
# # stack1_21 = slice_list.append(np.dstack(slices1_21))
# # stack1_31 = slice_list.append(np.dstack(slices1_31))
#
# #ras 2
slices2_11 = make_slices(arr2, 11,11)
slices2_21 = make_slices(arr2, 21,21)
slices2_31 = make_slices(arr2, 31,31)
#
# # stack2_11 = slice_list.append(np.dstack(slices2_11))
# # stack2_21 = slice_list.append(np.dstack(slices2_21))
# # stack2_31 = slice_list.append(np.dstack(slices2_31))
#
# #ras 3
slices3_11 = make_slices(arr3, 11,11)
slices3_21 = make_slices(arr3, 21,21)
slices3_31 = make_slices(arr3, 31,31)
#
# # stack3_11 = slice_list.append(np.dstack(slices3_11))
# # stack3_21 = slice_list.append(np.dstack(slices3_21))
# # stack3_31 = slice_list.append(np.dstack(slices3_31))
#
# #print(slices1_11[4].shape)
#
# counter = 0
#
# #def shdi(data): # data = slices of one window size and one image
# for slice in slices1_11:
#     results = []
#     counter +=1
#     cat_list =[1,2,3,5,11,13,17,18,19]
#     unique, counts = np.unique(slice, return_counts=True)
#     dict1 = dict(zip(unique, counts))
#     #print(dict1)
#     p_dict = {}
#     for cat in cat_list:                                        # loop through every category in the list
#         if cat in dict1:                                        # if this category is represented in the slice
#             p_dict.update({cat: dict1[cat]})                    # keep only the counts and keys that are in the list and the slice
#             #print(p_dict)
#     cat_sum = sum(p_dict.values())                              # get sum of all pixels containing one of the category values
#     for cat in cat_list:
#         if cat in dict1:
#             #prop_list.append(p_dict[cat]*100/cat_sum)
#             #prop_list.append(cat)
#             prop = p_dict[cat]*100/cat_sum
#             shdi = (prop * np.log(prop))
#             results.append(shdi)
#     shdi_fin = sum(results) * (-1)
#     print(shdi_fin)
# print(counter)
# out_data = np.ones((1000,1000)) * -99





# apply along axis function

########################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)


