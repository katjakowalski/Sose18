#Calculate for elevation and slope the mean, minimum and maximum values within the common extent of all three layers,
# and submit the numbers to moodle. Be aware of potential raster values in the topographic variables that may indicate
# NoData values but are not flagged as such (e.g., 65536 in the elevation layer).

import gdal
import glob
import os
import numpy as np

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
    print('X range',(min(LR_x_list)-max(UL_x_list))//gt[1])  # no of columns in x direction
    print('Y range', (min(UL_y_list)-max(LR_y_list))//gt[1]) # no of rows in y direction


rasteroverlap(file_list)

## DEM
dem_ras = gdal.Open('/Users/Katja/Documents/Studium/Sose18/week05/Assignment03 - data/DEM_Humboldt_sub.tif')
gt_dem = dem_ras.GetGeoTransform()
pr_dem = dem_ras.GetProjection()
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

# mask values of different arrays
arr_dem = np.ma.masked_where(arr_dem >= 8000, arr_dem, copy=True)
arr_slo = np.ma.masked_where(arr_slo < 0, arr_slo, copy=True)
arr_thp = np.ma.masked_where(arr_thp > 10000, arr_thp, copy=True)

print(' mean DEM:', round(np.mean(arr_dem),2),
      "\n", 'min DEM:', round(np.min(arr_dem),2),
      '\n', 'max DEM:', round(np.max(arr_dem),2),
      '\n', 'mean slope:', round(np.mean(arr_slo),2),
      '\n', 'min slope:', round(np.min(arr_slo),2),
      '\n', 'max slope:', round(np.max(arr_slo),2))


# Now take the elevation and slope layers only, and build a binary mask in which areas with elevation < 1000m and
# slope <30deg have the value ‘1’, and all other areas the value ‘0’. Write this binary mask into a new raster file
# and upload it to moodle.
# In addition, calculate the proportional area (two decimal digits) of raster cells having the value ‘1’ relative to
# the entire area. Upload this number to moodle.

arr_B1 = (arr_dem < 1000)                  # creates True/false array
arr_B2 = (arr_slo < 30)
arr_B12 = (arr_B2 == 1) & (arr_B1 == 1)     # creates T/F array where other array values are 1
arr_B12 = arr_B12*1                         # creates 1/0 array

print(arr_B12)
print("total px: ", np.count_nonzero(arr_B12 != 1)+np.count_nonzero(arr_B12 == 1),'\n' 
      "px 1: ", np.count_nonzero(arr_B12 == 1),'\n'
      "px 0: ", np.count_nonzero(arr_B12 == 0), '\n'
      "% px 1: ", round((np.count_nonzero(arr_B12 == 1)*100)/(np.count_nonzero(arr_B12 != 1)+np.count_nonzero(arr_B12 == 1)),2),'\n'
      "% px 0: ", (np.count_nonzero(arr_B12 == 0)*100)/(np.count_nonzero(arr_B12 != 1)+np.count_nonzero(arr_B12 == 1)))

# Save raster - code from class
# 0. Formulate an outputName
ras_B12 = root_folder + "dem_slope.tif"
# 1. Create a driver with which we write the output
drvR = gdal.GetDriverByName('GTiff')
# 2. Create the file (here: allthough exactly the same, we go through the syntax)
outDS = drvR.Create(ras_B12, 599, 1240, 1)
outDS.SetProjection(pr_dem)
outDS.SetGeoTransform(gt_dem)
# 3. Write the array into the newly generated file
outDS.GetRasterBand(1).WriteArray(arr_B12, 0, 0)#(array, offset_x, offset_y)



#For each of the areas of the different values in the THP raster dataset (i.e., 1997-2015) calculate the mean values
# slope and elevation with two decimal digits.
#Write the results into a comma-separated values file, and upload the file to moodle. Each row thereby should have the
# format Year, Mean_elev, Mean_slope

yearslist = list(range(1997,2016))

mean_list = list()
for i in yearslist:
    mean_list.extend((i, round(np.mean(arr_dem[arr_thp == i]),2)))
    mean_list.append((round(np.mean(arr_slo[arr_thp == i]),2)))

csv_array = np.array(mean_list)
csv_array = np.reshape(csv_array, (-1, 3))
print(csv_array)

np.savetxt('means.csv', csv_array, fmt='%.2f', delimiter=';', header='Year; Mean_elev; Mean_slope')


