import time
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("Starting process, time: " + starttime)
print("--------------------------------------------------------")
print("")
########################################################################
from osgeo import gdal, ogr, osr
import struct
import pandas as pd
import os
import numpy as np
import geopandas as gpd
import math
import random as rd
from shapely import wkt
########################################################################


baseFolder = "/Users/Katja/Documents/Studium/Sose18/week10/Assignment08_data/"
parcels = ogr.Open(baseFolder + "Parcels.shp", 1)
parcels_lyr = parcels.GetLayer()

roads = ogr.Open(baseFolder + "Roads.shp", 1)
roads_lyr = roads.GetLayer()

thp = ogr.Open(baseFolder + "TimberHarvestPlan.shp", 1)
thp_lyr = thp.GetLayer()

parcels_cs = parcels_lyr.GetSpatialRef()
feat = parcels_lyr.GetNextFeature()

mary = ogr.Open(baseFolder + "Marihuana_Grows.shp",1)
mary_lyr = mary.GetLayer()
mary_cs = mary_lyr.GetSpatialRef()

PL = ogr.Open(baseFolder + "PublicLands.shp", 1)
PL_lyr = PL.GetLayer()


i = 0
id = 0
out_df = pd.DataFrame(columns=["Parcel APN", "NR_GH-Plants", "NR_OD-Plants", "Dist_to_grow_m", "Km Priv. Road",
                               "Km Local Road", "Mean elevation", "PublicLand_YN", "Prop_in_THP"])
while feat:
    id += 1
    geom = feat.GetGeometryRef()
    apn = feat.GetField('APN')
    ###############################################################
    ######### Group 1 ############
    geom_par = feat.geometry().Clone()
    geom_par.Transform(osr.CoordinateTransformation(parcels_cs, mary_cs))

    mary_lyr.SetSpatialFilter(geom_par)
    total_gh = total_od = 0

    point_feat = mary_lyr.GetNextFeature()
    while point_feat:
        total_gh += point_feat.GetField('g_plants')
        total_od += point_feat.GetField('o_plants')
        point_feat = mary_lyr.GetNextFeature()
    mary_lyr.ResetReading()

    ######### Group 2 ############
    mary_lyr.SetSpatialFilter(geom_par)
    feature_count = mary_lyr.GetFeatureCount()
    #print("ID: " + str(id) + " Feature Count: " + str(feature_count))
    dist = 0
    if feature_count > 0:
        mary_lyr.SetSpatialFilter(None)
        bufferSize = 0
        exit = 0
        while exit == 0:
            bufferSize = bufferSize + 10
            buffer = geom_par.Buffer(bufferSize)
            mary_lyr.SetSpatialFilter(buffer)
            buffer_count = mary_lyr.GetFeatureCount()
            #print("Current buffer size: " + str(bufferSize) + "Current buffer count:" + str(buffer_count))
            if buffer_count > feature_count:
                exit += 1
                dist = bufferSize


    ######### Group 3 ############
    # Set filter for relevant road types
    roads_lyr.SetAttributeFilter("FUNCTIONAL IN ('Local Roads', 'Private')")
    # loop through two categories
    road_feat = roads_lyr.GetNextFeature()
    length_pr = length_lr = 0
    while road_feat:
        functional = road_feat.GetField('FUNCTIONAL')
        geom_roads = road_feat.GetGeometryRef()
        intersection = geom.Intersection(geom_roads)        # calculate intersection of road types and individual parcel
        length = intersection.Length()                      # get length of intersection
        if functional == 'Local Roads':
            length_lr = length/1000
        if functional == 'Private':
            length_pr = length/1000
        road_feat = roads_lyr.GetNextFeature()
    roads_lyr.ResetReading()

    # timber harvest plan > only use one year (overlapping geometries)
    thp_lyr.SetAttributeFilter("THP_YEAR = '1999'")
    thp_lyr.SetSpatialFilter(geom)                  # Set filter for parcel
    thp_feat = thp_lyr.GetNextFeature()
    area_parcel = geom.GetArea()                    # area of parcel
    thp_list = []

    # loop through selected features
    while thp_feat:
        geom_thp = thp_feat.GetGeometryRef()
        intersect_thp = geom.Intersection(geom_thp) # intersection of parcel and selected thp features
        area = intersect_thp.GetArea()              # area of intersected thp feature
        thp_list.append(area)                       # add area of thp feature to list
        thp_feat = thp_lyr.GetNextFeature()
    thp_sum = sum(thp_list)                         # sum up all thp features in parcel
    thp_prop = thp_sum/area_parcel

    ######### Group 4 ############
    # Public Lands
    public = 0
    PL_lyr.SetSpatialFilter(geom)
    if PL_lyr.GetFeatureCount() > 0:
        public = 1
    PL_lyr.SetSpatialFilter(None)

    # ############################################################# #
    out_df.loc[len(out_df) + 1] = [apn, total_gh, total_od, dist, length_pr, length_lr, 0, public, thp_prop ]  # insert further variables from other groups
    feat = parcels_lyr.GetNextFeature()

parcels_lyr.ResetReading()
out_df.to_csv("output_humboldt_county.csv", index=None, sep=',')


########################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)