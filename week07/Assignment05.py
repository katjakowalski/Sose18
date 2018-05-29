from osgeo import gdal, ogr, osr
import pandas as pd
import os
import numpy as np
import geopandas as gpd
from pyproj import Proj, transform
from math import modf
import random


root_folder = '/Users/Katja/Documents/Studium/Sose18/week07/Assignment05 - data/'

# convert
tmp = gpd.GeoDataFrame.from_file(root_folder + '/WDPA_May2018_polygons_GER_select10large.shp')
PA_Lambert = tmp.to_crs({'init':'EPSG:3035'})
PA_Lambert.to_file(root_folder + 'PA_Lambert2.shp')

# load shapefiles
driver = ogr.GetDriverByName("ESRI Shapefile")
PA = driver.Open(root_folder + '/PA_Lambert2.shp',1)
GER = driver.Open(root_folder + '/gadm36_GERonly.shp',1)
PO = driver.Open(root_folder + '/OnePoint.shp',1)

PA_lyr = PA.GetLayer()
GER_lyr = GER.GetLayer()
LS_lyr = PO.GetLayer()

PA_lyr.GetSpatialRef()                                                                                 #EPSG 4326 (WSG84)


inProj = Proj(init='epsg:32633')
outProj = Proj(init='epsg:3035')
x1,y1 = 387989.426864,5819549.72673
x2,y2 = transform(inProj,outProj,x1,y1)
#print(x2, y2)


for i in PA_lyr:
    geom = i.GetGeometryRef()
    (minX, maxX, minY, maxY) = geom.GetEnvelope()
    resxmax = (abs(x2 - minX))/30
    resxmin = (abs(x2 - maxX))/30
    resymax = (abs(y2 - maxY))/30
    resymin = (abs(y2 - minY))/30

    if (resxmax).is_integer():
        FmaxX = maxX
    else:
        resx1 = modf(resxmax)
        FmaxX = maxX + (1 - (round(resx1[0],2)))

    if (resxmin).is_integer():
        FminX = minX
    else:
        resx2 = modf(resxmin)
        FminX = minX - (round(resx2[0],2))

    if (resymax).is_integer():
        FmaxY = maxY
    else:
        resy1 = modf(resymax)
        FmaxY = maxY + (1 - (round(resy1[0],2)))

    if (resymin).is_integer():
        FminY = minY
    else:
        resy2 = modf(resymin)
        FminY = minY - (round(resy2[0],2))
    print('X max:', FmaxX, 'X min:', FminX, 'Y max:', FmaxY, 'Y min:', FminY, resx1[0], resx2[0], resy1[0], resy2[0])

print(np.arange(4548368.992322878, 4600697.42988372, 30))



