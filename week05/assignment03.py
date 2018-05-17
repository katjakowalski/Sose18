#Calculate for elevation and slope the mean, minimum and maximum values within the common extent of all three layers,
# and submit the numbers to moodle. Be aware of potential raster values in the topographic variables that may indicate
# NoData values but are not flagged as such (e.g., 65536 in the elevation layer).


    #In addition, calculate the proportional area (two decimal digits) of raster cells having the value ‘1’ relative to
    # the entire area. Upload this number to moodle.

import gdal
import glob
import os
import numpy as np
import numpy.ma as ma
import gdal

#pr = dem_ras.GetProjection()
#cols = dem_ras.RasterXSize
#rows = dem_ras.RasterYSize
#dem_arr = dem.ReadAsArray(0,0, cols, rows) # origin x, origin y, slice size x, slice size y > get subset in the same way

root_folder = "/Users/Katja/Documents/Studium/Sose18/week05/Assignment03 - data/"
file_list = glob.glob(os.path.join(root_folder, '*.tif'))

def rasteroverlap(file_list):
    UL_x_list = list()
    UL_y_list = list()
    LR_x_list = list()
    LR_y_list = list()
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
        print(os.path.basename(i), 'Upper Left X:',UL_x, 'Upper Left Y:', UL_y, 'Lower Right X:', LR_x, 'Lower Right Y:', LR_y)
    print('UL X:', max(UL_x_list),'UL Y:', min(UL_y_list))
    print('LR X:', min(LR_x_list),'LR Y:', max(LR_y_list))
    print('X range',(min(LR_x_list)-max(UL_x_list))/gt[1])  # no of columns in x direction
    print('Y range', (min(UL_y_list)-max(LR_y_list))/gt[1]) # no of rows in y direction


rasteroverlap(file_list)

## DEM
dem_ras = gdal.Open('/Users/Katja/Documents/Studium/Sose18/week05/Assignment03 - data/DEM_Humboldt_sub.tif')
gt_dem = dem_ras.GetGeoTransform()
inv_dem = gdal.InvGeoTransform(gt_dem)
#print(inv_dem)

offsets_dem = gdal.ApplyGeoTransform(inv_dem, 1399618.9749825108, 705060.6257949192)
xoff1, yoff1 = map(int, offsets_dem)
arr_dem = dem_ras.ReadAsArray(xoff1, yoff1, 599, 1240)
#print(arr_dem)

## Slope
slope_ras = gdal.Open('/Users/Katja/Documents/Studium/Sose18/week05/Assignment03 - data/SLOPE_Humboldt_sub.tif')
gt_slo = slope_ras.GetGeoTransform()

inv_slo = gdal.InvGeoTransform(gt_slo)
offsets_slo = gdal.ApplyGeoTransform(inv_slo, 1399618.9749825108, 705060.6257949192)
xoff2, yoff2 = map(int, offsets_slo)
arr_slo = slope_ras.ReadAsArray(xoff2, yoff2, 599, 1240)
#print(arr_slo)


## THP
thp_ras = gdal.Open('/Users/Katja/Documents/Studium/Sose18/week05/Assignment03 - data/THP_Humboldt_sub.tif')
gt_thp = thp_ras.GetGeoTransform()

inv_thp = gdal.InvGeoTransform(gt_thp)
offsets_thp = gdal.ApplyGeoTransform(inv_thp, 1399618.9749825108, 705060.6257949192)
xoff3, yoff3 = map(int, offsets_thp)
arr_thp = thp_ras.ReadAsArray(xoff3, yoff3, 599, 1240)
#print(arr_thp)

arr_dem = ma.masked_where(arr_dem >= 8000, arr_dem)
arr_slo = ma.masked_where(arr_slo < 0, arr_slo)
arr_thp = ma.masked_where(arr_thp > 10000, arr_thp)
print(' mean DEM:', np.mean(arr_dem),
      "\n", 'min DEM:', np.min(arr_dem),
      '\n', 'max DEM:', np.max(arr_dem),
      '\n', 'mean slope:', np.mean(arr_slo),
      '\n', 'min slope:', np.min(arr_slo),
      '\n', 'max slope:', np.max(arr_slo))




# Now take the elevation and slope layers only, and build a binary mask in which areas with elevation < 1000m and
# slope <30deg have the value ‘1’, and all other areas the value ‘0’. Write this binary mask into a new raster file
# and upload it to moodle.


arr_stack = ma.dstack((arr_dem, arr_slo))


#GetGeoTransform > have to create a new one for final output file  out_ds.SetProjection(old_projectionvariable) (Projection)
# /out_ds.SetGeoTransform(new_gt_object) (pixel size)

