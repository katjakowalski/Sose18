# I did not check if samples are at least 90m away from each other in x or y direction


######################################################################################
from osgeo import gdal, ogr, osr
import pandas as pd
import os
import numpy as np
import geopandas as gpd
from pyproj import Proj, transform
import math
import random as rd
from shapely import wkt
######################################################################################

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
    PA_geom = i.geometry().Clone()
    (minX, maxX, minY, maxY) = PA_geom.GetEnvelope()
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
    while  len(count_list) < 1:                                    # sample some more to later check for distance
        # sample within step ranges
        x_step = rd.randint(step_x_min, step_x_max)
        y_step = rd.randint(step_y_min, step_y_max)
        # get final coordinate
        x_c = x_LS + x_step * 30
        y_c = y_LS + y_step * 30
        spnt = ogr.Geometry(ogr.wkbPoint)
        spnt.AddPoint(x_c, y_c)
        if PA_geom.Contains(spnt):
            coord_wkt = wkt.loads(str(spnt))
            PA_wkt = wkt.loads(str(PA_geom))
            if PA_wkt.boundary.distance(coord_wkt) >= 64:               # check if distance to nearest boundary is >= 64m (value from group work)
                df.loc[len(df) + 1] = [key, count, x_c, y_c]
                count_list.append(1)
                print('sample added')
            else: print('Point too close to PA boundary')
        else: print('Point outside PA')
    count_list = list()

print(df.count())
df.to_csv('test.csv')

# create shapefile and layer
driver = ogr.GetDriverByName('ESRI Shapefile')
data_source = driver.CreateDataSource('sample_blocks.shp')
srs = osr.SpatialReference()
srs.ImportFromEPSG(3050)
layer = data_source.CreateLayer("sample_blocks", srs, ogr.wkbPolygon)

# add fields
field0 = ogr.FieldDefn("ID_coord", ogr.OFTInteger)
layer.CreateField(field0)

field1 = ogr.FieldDefn("ID", ogr.OFTInteger)
layer.CreateField(field1)

field2 = ogr.FieldDefn("PA", ogr.OFTString)
layer.CreateField(field2)

defn = layer.GetLayerDefn()

# create kml file
driver2 = ogr.GetDriverByName('KML')
data_source2 = driver2.CreateDataSource('sample_blocks_kml.kml')
srs2 = osr.SpatialReference()
srs2.ImportFromEPSG(3050)
layer2 = data_source2.CreateLayer('sample_blocks_kml', srs2, ogr.wkbPolygon)
layer2.CreateField(field0)
layer2.CreateField(field1)
layer2.CreateField(field2)

defn2 = layer2.GetLayerDefn()

poly_compl = ogr.Geometry(ogr.wkbMultiPolygon)
for index, row in df.iterrows():
    x0 = row['X']
    y0 = row['Y']
    ID_coord = row['ID']
    PA = row['PA_name']
    # calculate 4 x and y values to get every coordinate for the 9 polygons
    x1 = x0 - 45
    x2 = x0 - 15
    x3 = x0 + 15
    x4 = x0 + 45

    y1 = y0 - 45
    y2 = y0 - 15
    y3 = y0 + 15
    y4 = y0 + 45

    print(x0, y0)
    print(x1, y1)
    print(x2, y2)
    print(x3, y3)
    print(x4, y4)
####################################################
    # polygon: 1st row left
    ring1 = ogr.Geometry(ogr.wkbLinearRing)
    ring1.AddPoint(x1, y4) # go clockwise
    ring1.AddPoint(x2, y4)
    ring1.AddPoint(x2, y3)
    ring1.AddPoint(x1, y3)
    ring1.AddPoint(x1, y4) # close ring

    poly1 = ogr.Geometry(ogr.wkbPolygon)
    poly1.AddGeometry(ring1)

    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly1)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 1)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly1)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 1)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################
    # polygon: 1st row middle
    ring2 = ogr.Geometry(ogr.wkbLinearRing)
    ring2.AddPoint(x2, y4)
    ring2.AddPoint(x3, y4)
    ring2.AddPoint(x3, y3)
    ring2.AddPoint(x2, y3)
    ring2.AddPoint(x2, y4)

    poly2 = ogr.Geometry(ogr.wkbPolygon)
    poly2.AddGeometry(ring2)

    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly2)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 2)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly2)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 2)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################

    # polygon: 1st row right
    ring3 = ogr.Geometry(ogr.wkbLinearRing)
    ring3.AddPoint(x3, y4)
    ring3.AddPoint(x4, y4)
    ring3.AddPoint(x4, y3)
    ring3.AddPoint(x3, y3)
    ring3.AddPoint(x3, y4)

    poly3 = ogr.Geometry(ogr.wkbPolygon)
    poly3.AddGeometry(ring3)
    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly3)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 3)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly3)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 3)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################

    # polygon: 2nd row left
    ring4 = ogr.Geometry(ogr.wkbLinearRing)
    ring4.AddPoint(x1, y3)
    ring4.AddPoint(x2, y3)
    ring4.AddPoint(x2, y2)
    ring4.AddPoint(x1, y2)
    ring4.AddPoint(x1, y3)

    poly4 = ogr.Geometry(ogr.wkbPolygon)
    poly4.AddGeometry(ring4)
    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly4)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 4)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly4)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 4)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################

    # polygon: 2nd row middle
    ring5 = ogr.Geometry(ogr.wkbLinearRing)
    ring5.AddPoint(x2, y3)
    ring5.AddPoint(x3, y3)
    ring5.AddPoint(x3, y2)
    ring5.AddPoint(x2, y2)
    ring5.AddPoint(x2, y3)

    poly5 = ogr.Geometry(ogr.wkbPolygon)
    poly5.AddGeometry(ring5)

    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly5)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 5)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly5)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 5)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################

    # polygon: 2nd row right
    ring6 = ogr.Geometry(ogr.wkbLinearRing)
    ring6.AddPoint(x3, y3)
    ring6.AddPoint(x4, y3)
    ring6.AddPoint(x4, y2)
    ring6.AddPoint(x3, y2)
    ring6.AddPoint(x3, y3)

    poly6 = ogr.Geometry(ogr.wkbPolygon)
    poly6.AddGeometry(ring6)

    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly6)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 6)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly6)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 6)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################


    # polygon: 3rd row left
    ring7 = ogr.Geometry(ogr.wkbLinearRing)
    ring7.AddPoint(x1, y2)
    ring7.AddPoint(x2, y2)
    ring7.AddPoint(x2, y1)
    ring7.AddPoint(x1, y1)
    ring7.AddPoint(x1, y2)

    poly7 = ogr.Geometry(ogr.wkbPolygon)
    poly7.AddGeometry(ring7)
    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly7)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 7)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly7)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 7)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################

    # polygon: 3rd row middle
    ring8 = ogr.Geometry(ogr.wkbLinearRing)
    ring8.AddPoint(x2, y2)
    ring8.AddPoint(x3, y2)
    ring8.AddPoint(x3, y1)
    ring8.AddPoint(x2, y1)
    ring8.AddPoint(x2, y2)

    poly8 = ogr.Geometry(ogr.wkbPolygon)
    poly8.AddGeometry(ring8)
    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly8)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 8)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly8)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 8)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################
    # polygon: 3rd row right
    ring9 = ogr.Geometry(ogr.wkbLinearRing)
    ring9.AddPoint(x3, y2)
    ring9.AddPoint(x4, y2)
    ring9.AddPoint(x4, y1)
    ring9.AddPoint(x3, y1)
    ring9.AddPoint(x3, y2)

    poly9 = ogr.Geometry(ogr.wkbPolygon)
    poly9.AddGeometry(ring9)
    # add feature to shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(poly9)
    feat.SetField('ID_coord', ID_coord)
    feat.SetField('ID', 9)
    feat.SetField('PA', PA)
    layer.CreateFeature(feat)

    feat2 = ogr.Feature(defn2)
    feat2.SetGeometry(poly9)
    feat2.SetField('ID_coord', ID_coord)
    feat2.SetField('ID', 9)
    feat2.SetField('PA', PA)
    layer2.CreateFeature(feat2)
####################################################
data_source = None
data_source2 = None


