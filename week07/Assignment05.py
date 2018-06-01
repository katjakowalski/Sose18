from osgeo import gdal, ogr, osr
import pandas as pd
import os
import numpy as np
import geopandas as gpd
from pyproj import Proj, transform
import math
import random as rd


root_folder = '/Users/Katja/Documents/Studium/Sose18/week07/Assignment05 - data/'

# convert
tmp = gpd.GeoDataFrame.from_file(root_folder + '/WDPA_May2018_polygons_GER_select10large.shp')
PA_Lambert = tmp.to_crs({'init':'EPSG:3035'})
PA_Lambert.to_file(root_folder + 'PA_Lambert2.shp')

tmp = gpd.GeoDataFrame.from_file(root_folder + '/OnePoint.shp')
point1 = tmp.to_crs({'init':'EPSG:3035'})
point1.to_file(root_folder + 'point.shp')

# load shapefiles
driver = ogr.GetDriverByName("ESRI Shapefile")
PA = driver.Open(root_folder + '/PA_Lambert2.shp',1)
PO = driver.Open(root_folder + '/point.shp',1)

PA_lyr = PA.GetLayer()
LS_lyr = PO.GetLayer()

PA_lyr.GetSpatialRef()                                                                                #EPSG 4326 (WSG84)

# get center coordinate from reference pixel
Coords= LS_lyr.GetExtent()
x_LS = Coords[0]
y_LS = Coords[2]

#sample_count = {}  # create dictionary

#sample_count = list()

df = pd.DataFrame(columns=['PA_name', 'ID', 'X', 'Y'])
print(df)
count = 0
for i in PA_lyr:
    geom = i.GetGeometryRef()
    (minX, maxX, minY, maxY) = geom.GetEnvelope()
    # how many pixels fit between point and min/max value
    x_min = (minX - x_LS)/30
    x_max = (maxX - x_LS)/30
    y_max = (maxY - y_LS)/30
    y_min = (minY - y_LS)/30#
    # round values:
        # xmin: abrunden (positive Zahl), aufrunden (negative Zahl)
        # xmax: aufrunden (positive Zahl), abrunden (negative Zahl)
        # ymin: abrunden (positive Zahl), aufrunden (negative Zahl)
        # ymax: aufrunden (positive Zahl), abrunden (negative Zahl)
    if x_min > 0:
        step_x_min = math.floor(x_min)
    elif x_min == 0:
        step_x_min =x_min
    else:
        step_x_min = math.ceil(x_min)

    if y_min > 0:
        step_y_min = math.floor(y_min)
    elif y_min == 0:
        step_x_min =y_min
    else:
        step_y_min = math.ceil(y_min)

    if x_max > 0:
        step_x_max = math.ceil(x_max)
    elif x_max == 0:
        step_x_max = x_max
    else:
        step_x_max = math.floor(x_max)

    if y_max > 0:
        step_y_max = math.ceil(y_max)
    elif y_max == 0:
        step_y_max = y_max
    else:
        step_y_max = math.floor(y_max)

    #sample_count.append(i.GetField('NAME'))
    key = i.GetField('NAME')
    count_list = list()
    count = count + 1
    while  len(count_list) < 50:
        # sample within step ranges
        x_step = rd.randint(step_x_min, step_x_max)
        y_step = rd.randint(step_y_min, step_y_max)
        # get final coordinate
        x_c = x_LS + x_step * 30
        y_c = y_LS + y_step * 30
        spnt = ogr.Geometry(ogr.wkbPoint)
        spnt.AddPoint(x_c, y_c)
        if geom.Contains(spnt):
            df.loc[len(df)+1] = [key, count, x_c, y_c]
            count_list.append(1)
    count_list = list()

print(pd.df.count())





# more than 64m from border of PA
# within PA
# at least 90 m in x or y direction from next point


    #x_coord = rd.randrange(x_min, x_max, 30)
    #x_coord = rd.randrange(y_min, y_max, 30)
    #print('x_min:', x_min, 'x_max:', x_max, 'y_min:', y_min, 'y_max:', y_max)
    #, 'x_sample:', x_coord, 'y_sample:', y_coord)





