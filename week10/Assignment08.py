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

###################################################################################################################
def TransformGeometry(geometry, target_sref):
    '''Returns cloned geometry, which is transformed to target spatial reference'''
    geom_sref = geometry.GetSpatialReference()
    transform = osr.CoordinateTransformation(geom_sref, target_sref)
    geom_trans = geometry.Clone()
    geom_trans.Transform(transform)
    return geom_trans


def SpatialReferenceFromRaster(ds):
    '''Returns SpatialReference from raster dataset'''
    pr = ds.GetProjection()
    sr = osr.SpatialReference()
    sr.ImportFromWkt(pr)
    return sr


def CopySHPDisk(layer, outpath):
    drvV = ogr.GetDriverByName('ESRI Shapefile')
    outSHP = drvV.CreateDataSource(outpath)  # outpath
    lyr = layer  # .GetLayer() #shape
    sett90LYR = outSHP.CopyLayer(lyr, 'lyr')
    del lyr, sett90LYR, outSHP

###################################################################################################################

baseFolder = "/Users/Katja/Documents/Studium/Sose18/week10/Assignment08_data/"


parcels = ogr.Open(baseFolder + "Parcels.shp", 1)
parcels_lyr = parcels.GetLayer()
p_srs = parcels_lyr.GetSpatialRef()
p_def = parcels_lyr.GetLayerDefn()

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

dem = gdal.Open(baseFolder + "DEM_Humboldt.tif")
gt = dem.GetGeoTransform()
pr = dem.GetProjection()

sr_raster = SpatialReferenceFromRaster(dem)


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
    thp_lyr.SetSpatialFilter(None)
    ######### Group 4 ############
    # Public Lands
    public = 0
    PL_lyr.SetSpatialFilter(geom)
    if PL_lyr.GetFeatureCount() > 0:
        public = 1
    PL_lyr.SetSpatialFilter(None)

#######################################################################################################################
    # Transform Coordinate System
    p_geom_trans = TransformGeometry(geom, sr_raster)
    # Get Coordinates of polygon envelope
    x_min, x_max, y_min, y_max = p_geom_trans.GetEnvelope()

    # Create dummy shapefile to story features geometry in (necessary for rasterizing)
    drv_mem = ogr.GetDriverByName('Memory')
    ds = drv_mem.CreateDataSource("")
    ds_lyr = ds.CreateLayer("", SpatialReferenceFromRaster(dem), ogr.wkbPolygon)
    featureDefn = ds_lyr.GetLayerDefn()
    out_feat = ogr.Feature(featureDefn)
    out_feat.SetGeometry(p_geom_trans)
    ds_lyr.CreateFeature(out_feat)
    out_feat = None
    # CopySHPDisk(ds_lyr, "tryout.shp") #If you wish to check the shp

    # Create the destination data source
    x_res = math.ceil((x_max - x_min) / gt[1])
    y_res = math.ceil((y_max - y_min) / gt[1])
    target_ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, gdal.GDT_Byte)
    target_ds.GetRasterBand(1).SetNoDataValue(-9999)
    target_ds.SetProjection(pr)
    target_ds.SetGeoTransform((x_min, gt[1], 0, y_max, 0, gt[5]))

    # Rasterization
    gdal.RasterizeLayer(target_ds, [1], ds_lyr,
                        burn_values=[1], options = ['ALL_TOUCHED=TRUE'])  # ['ALL_TOUCHED=TRUE'] command necessary, however does not work yet
    target_array = target_ds.ReadAsArray()
    # target_ds = None

    # Convert data from the DEM to the extent of the envelope of the polygon (to array)
    inv_gt = gdal.InvGeoTransform(gt)
    offsets_ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
    off_ul_x, off_ul_y = map(int, offsets_ul)
    raster_np = np.array(dem.GetRasterBand(1).ReadAsArray(off_ul_x, off_ul_y, x_res, y_res))

    # Calculate the mean of the array with masking
    test_array = np.ma.masked_where(target_array < 1, target_array)
    raster_masked = np.ma.masked_array(raster_np, test_array.mask)
    dem_mean = np.mean(raster_masked)

#######################################################################################################################


    # ############################################################# #
    out_df.loc[len(out_df) + 1] = [apn, total_gh, total_od, dist, length_pr, length_lr, dem_mean, public, thp_prop ]  # insert further variables from other groups
    feat = parcels_lyr.GetNextFeature()

parcels_lyr.ResetReading()
out_df.to_csv("output_humboldt_county.csv", index=None, sep=',')


########################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)