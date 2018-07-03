import time

starttime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
print("Starting process, date and time: " + starttime)
print("--------------------------------------------------------")
print("")

#####################################################################################

from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import math
from joblib import Parallel, delayed
import multiprocessing
import os
import glob

#####################################################################################

baseFolder = "/Users/Katja/Documents/Studium/Sose18/week12/Assignment10_data/"


rasterPath = glob.glob(os.path.join(baseFolder + "*.tif"))

windowSize = [11,21,31]


raster_list = list()
for i in rasterPath:
    for window in windowSize:
        liste = list()
        liste.append(i)
        liste.append(window)
        raster_list.append(liste)

print(raster_list)

# ####################################### FUNCTIONS ########################################################### #
def calcSHDI(array):
	arraySize = array.size
	SHDI = 0
	vals = [1, 2, 3, 5]
	array = np.where(array == 17, 1, array)  # reclassify open woodlands into forest
	for val in vals:
		count = (array == val).sum()
		# Check if value in in there, if not (i.e., count=0) then skip, because otherwise the ln will not be calculated
		if count > 0:
			prop = count / arraySize
			SHDI = SHDI + (prop * np.log(prop))
		else:
			SHDI = SHDI
	SHDI = - SHDI
	return SHDI

rasters = glob.glob(os.path.join(baseFolder + "*.tif"))


# ####################################### START PROCESSING #################################################### #
# (1) get the number of files

def workerfunction(job):
    drvR = gdal.GetDriverByName("GTiff")
    rasterPath = job[0]
    ds = gdal.Open(rasterPath)
    print("Processing raster: ", rasterPath)
    gt = ds.GetGeoTransform()
    pr = ds.GetProjection()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    ds_array = ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    rad = job[1]
    print("window-size: ", str(rad))
# Define offset in x- and y-direction
    offset_xy = int(rad / 2)
# Build the output array
    startRow = int(rad / 2)
    startCol = int(rad / 2)
    endRow = rows - startRow - 1
    endCol = cols - startCol - 1
    dim01_y = endRow - startRow  # nr. of indices in y-direction
    dim01_x = endCol - startCol  # nr. of indices in x-direction
    dim02 = rad * rad  # window-size
    sliced_array = np.zeros((dim01_y * dim01_x, dim02), dtype=np.float)
# Populate the array
    index = 0  # set a manual counter to step through the different slices
    for row in range(startRow, endRow):
        for col in range(startCol, endCol):
                    # calculate array coordinates of corner
            y_min = row - offset_xy
            y_max = row - offset_xy + rad
            x_min = col - offset_xy
            x_max = col - offset_xy + rad
            #print(x_min, y_min, x_max, y_max)
            # with .flatten() you remove any dimensions from your ndarray
            sliced_array[index, :] = ds_array[y_min : y_max, x_min : x_max].flatten()
            index += 1
    # calculate the index based on the function
    SHDI = np.apply_along_axis(calcSHDI, 1, sliced_array)
    # reshape and write to output-array
    SHDI = np.reshape(SHDI, ((endRow - startRow), (endCol - startCol)))
    out_array = np.zeros((rows, cols), dtype=float)
    out_array[startRow:endRow, startCol:endCol] = SHDI
    # write to output
    outname = job[0]
    outname = outname.replace(".tif", "_SHDI_"+str(rad)+".tif")
    SHDI_out = drvR.Create(outname, cols, rows, 1, gdal.GDT_Float32)
    SHDI_out.SetProjection(pr)
    SHDI_out.SetGeoTransform(gt)
    SHDI_out.GetRasterBand(1).WriteArray(out_array, 0, 0)


Parallel(n_jobs=3)(delayed(workerfunction)(i) for i in raster_list)
# set ending time ############################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")