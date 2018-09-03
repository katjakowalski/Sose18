import time

starttime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
print("Starting process, date and time: " + starttime)
print("--------------------------------------------------------")
print("")

#####################################################################################
# import packages
from osgeo import gdal, ogr, osr
import numpy as np
import random as rd
import struct
from Tools import list_files, corner_coordinates, return_raster_values
import os
########################################################################################################################
# I did not include this function in the tools package since it is not generalized
def fill_shapefile(x, y):
    '''fills shapefile with points (x,y), shapefile and fields have to be created before applying the function'''
    pt = ogr.Geometry(ogr.wkbPoint)
    pt.AddPoint(x,y)                # use x and y of transformed sample coordinates
    feat = ogr.Feature(defn)
    feat.SetGeometry(pt)
    feat.SetField('UID', point_id)      # modify fields and values to be stored here
    feat.SetField('VCF', val_veg)
    layer.CreateFeature(feat)
    feat = None
########################################################################################################################

# define working directory
os.chdir("/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task01_data/")

# get all files in subfolders of data
root_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task01_data/"
file_list = list_files(root_folder)

# create list with all raster files (tiles)
tile_1 = [i for i in file_list if '38999' in i]
tile_2 = [i for i in file_list if '39999' in i]
tile_3 = [i for i in file_list if '40999' in i]
tile_4 = [i for i in file_list if '41999' in i]
tile_list = tile_1 + tile_2 + tile_3 + tile_4
tile_list = [i for i in tile_list if '.hdr' not in i]

# gets corner coordinates = sample boundary (see function)
x_min, x_max, y_min, y_max = corner_coordinates(tile_list)

# defines coordinate transformation Landsat/Sentinel data <> Vegetation data
ras_veg = gdal.Open(root_folder + '/2000_VCF/20S_070W.tif')
ras = ras_veg.GetRasterBand(1)
pr_veg = ras_veg.GetProjection()                                    # get projection from Veg. raster
target_SR = osr.SpatialReference()                                  # create empty spatial reference
target_SR.ImportFromWkt(pr_veg)                                     # get spatial reference from projection of raster

ras_LS = gdal.Open(root_folder + '/2015_L8_doy015/Tile_x18999_y38999_1000x1000_2014-2015_CHACO_PBC_multiYear_Imagery.bsq')
pr_LS = ras_LS.GetProjection()                                      # get projection from Veg. raster
source_SR = osr.SpatialReference()                                  # create empty spatial reference
source_SR.ImportFromWkt(pr_LS)                                      # get spatial reference from projection of raster
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)     # transformation rule
gt_ras = ras_veg.GetGeoTransform()                                  # get information from vegetation raster

# creates output shapefile and layer
driver = ogr.GetDriverByName('ESRI Shapefile')
data_source = driver.CreateDataSource('Kowalski_Katja_MAP-task01_randomPoints.shp')
srs = osr.SpatialReference()
srs.ImportFromEPSG(102033)
layer = data_source.CreateLayer("Kowalski_Katja_MAP-task01_randomPoints", srs, ogr.wkbPoint)

# creates fields 'UID' and 'VCF' in shapefile
field0 = ogr.FieldDefn("UID", ogr.OFTInteger)
layer.CreateField(field0)

field3 = ogr.FieldDefn("VCF", ogr.OFTInteger)
layer.CreateField(field3)

defn = layer.GetLayerDefn()

# create lists to track sampling in classes, store ID and raster band values
count_list1 = 0
count_list2 = 0
count_list3 = 0
count_list4 = 0
count_list5 = 0
pt_list = []
arr_list_final = []
point_id = 0


while count_list1 < 100 or count_list2 < 100 or count_list3 < 100 or count_list4 < 100 or count_list5 < 100:
    x1 = rd.uniform(x_min, x_max)                                   # sample random value in x range
    y1 = rd.uniform(y_min, y_max)                                   # sample random value in y range
    point = ogr.Geometry(ogr.wkbPoint)                              # create empty geometry and then add point geometry from coordinates
    point.AddPoint(x1, y1)

    # extract values from vegetation raster
    coord_cl = point.Clone()                                        # clone sample geometry
    coord_cl.Transform(coordTrans)                                  # apply coordinate transformation
    x, y = coord_cl.GetX(), coord_cl.GetY()                         # get x and y coordinates of transformed sample point

    #calculate absolute raster coordinates:
    px_ras = int((x - gt_ras[0]) / gt_ras[1])
    py_ras = int((y - gt_ras[3]) / gt_ras[5])

    # extract information from raster and unpack values
    struc_ras = ras.ReadRaster(px_ras, py_ras, 1, 1)
    if struc_ras is None:
        val_veg = struc_ras
    else:
        val_ras = struct.unpack('b', struc_ras)
        val_veg = val_ras[0]

    # following blocks of code:
    # - checks in which stratum sample belongs based on VCF value and if more samples are needed in this stratum
    # - extracts raster values (see function) and adds point and values (VCF, UID) to shapefile
    # (see function at top of code)

    if 0 <= val_veg <= 20 and count_list1 < 100:
        point_id += 1
        count_list1 += 1
        arr_list1 = return_raster_values(x1,y1,tile_list)
        arr_list_final.append(arr_list1)
        fill_shapefile(x1,y1)
        pt_list.append(val_veg)

    elif 21 <= val_veg <= 40 and count_list2 < 100:
        point_id += 1
        count_list2 += 1
        arr_list2 = return_raster_values(x1, y1, tile_list)
        arr_list_final.append(arr_list2)
        fill_shapefile(x1, y1)
        pt_list.append(val_veg)

    elif 41 <= val_veg <= 60 and count_list3 < 100:
        point_id += 1
        count_list3 += 1
        arr_list3 = return_raster_values(x1, y1, tile_list)
        arr_list_final.append(arr_list3)
        fill_shapefile(x1, y1)
        pt_list.append(val_veg)

    elif 61 <= val_veg <= 80 and count_list4 < 100:
        point_id += 1
        count_list4 += 1
        arr_list4 = return_raster_values(x1, y1, tile_list)
        arr_list_final.append(arr_list4)
        fill_shapefile(x1, y1)
        pt_list.append(val_veg)

    elif 81 <= val_veg <= 100 and count_list5 < 100:
        point_id += 1
        count_list5 += 1
        arr_list5 = return_raster_values(x1, y1, tile_list)
        arr_list_final.append(arr_list5)
        fill_shapefile(x1, y1)
        pt_list.append(val_veg)


# create array from list of lists
arr_tr = np.asarray(arr_list_final)                   # create array of shape 68 columns (= bands) x 500 rows (=samples)
arr_tr_cl = np.asarray(pt_list)                       # create array of shape 1 column x 500 rows with VCF values

# write arrays to disk
np.save("Kowalski_Katja_MAP-task01_np-array_x-values.npy", arr_tr)
np.save("Kowalski_Katja_MAP-task01_np-array_y-values.npy", arr_tr_cl)

#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")