import time

starttime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
print("Starting process, date and time: " + starttime)
print("--------------------------------------------------------")
print("")

########################################################################################################################
# import packages
from osgeo import gdal, ogr, osr
import pandas as pd
import geopandas as gpd
from functools import reduce
import os
import shutil
from Tools import dissolve_polygons
########################################################################################################################

os.chdir("/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task02_data/")
root_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task02_data/"

# create folder to store data temporarily
store_folder = "/Users/Katja/Documents/Studium/Sose18/MAP/Geoprocessing-in-python_MAP2018_data/Task02_data/temp/"
if not os.path.exists(store_folder):
    os.makedirs(store_folder)

# open original shapefiles
driver = ogr.GetDriverByName("ESRI Shapefile")
country_shp = driver.Open(root_folder + '/ZonalShape_Countries_Europe_NUTS1_multipart.shp', 1)
dam_shp = driver.Open(root_folder + '/GRanD_dams_v1_1_Europe-sub.shp',1)
road_shp = driver.Open(root_folder + '/gRoads-v1-Europe-sub.shp',0)

countries_lyr = country_shp.GetLayer()
roads_lyr = road_shp.GetLayer()
dams_lyr = dam_shp.GetLayer()

# get memory driver for raster and shapefile data
tif_driver = gdal.GetDriverByName('MEM')
shp_driver = ogr.GetDriverByName('Memory')

# reprojects road and country shapefiles to epsg 3035 (Lambert Equal Area) to work with spatial resolution in m
tmp = gpd.GeoDataFrame.from_file(root_folder + '/gRoads-v1-Europe-sub.shp')
roads_3035 = tmp.to_crs({'init':'EPSG:3035'})
roads_3035.to_file(store_folder + 'roads_3035.shp')
ro = driver.Open(store_folder + '/roads_3035.shp',0)
roads_3035 = ro.GetLayer()

tmp = gpd.GeoDataFrame.from_file(root_folder + '/ZonalShape_Countries_Europe_NUTS1_multipart.shp')
countries_3035 = tmp.to_crs({'init':'EPSG:3035'})
countries_3035.to_file(store_folder + 'countries_3035.shp')
co = driver.Open(store_folder + '/countries_3035.shp',0)
countries_3035 = co.GetLayer()

# coordinate transformations
source_SR = dams_lyr.GetSpatialRef()
target_SR = countries_lyr.GetSpatialRef()
coordTrans= osr.CoordinateTransformation(source_SR, target_SR)

source_SR = countries_lyr.GetSpatialRef()
target_SR = roads_lyr.GetSpatialRef()
coordTrans_roads = osr.CoordinateTransformation(source_SR, target_SR)

# dissolves country polygons based on name:
dissolve_polygons(store_folder, '/countries_3035.shp', '/countries_3035_diss.shp')
co_shp = driver.Open(store_folder + '/countries_3035_diss.shp',1)
countries_3035_diss = co_shp.GetLayer()

# Following code block:
# - creates 3 rasters for each country (rasterized roads, proximity raster for roads, raster with country extent)
# - creates 1 shapefile which contains the respective country
# - calculates statistics for each country based on proximity raster

cellsize = 100                                          # defines cellsize for all rasters
roads_list = []                                         # list to store max and mean distance to road for each country
o_feat = countries_3035_diss.GetNextFeature()
while o_feat:
    x_min, x_max, y_min, y_max = o_feat.geometry().GetEnvelope()    # gets bounding coordinates of country
    name = o_feat.GetField('state')

    roads_3035.SetSpatialFilterRect(x_min, y_min, x_max, y_max)     # sets spatial filter on road layer
    cols = int((x_max - x_min) / cellsize)                          # calculates number of columns and rows to create new raster
    rows = int((y_max - y_min) / cellsize)

    # creates raster of road shapefile
    road_ds = tif_driver.Create(root_folder + 'road_ds.tif', cols, rows)  # creates new empty raster with col, row specifications
    road_ds.SetProjection(roads_3035.GetSpatialRef().ExportToWkt())       # assigns projection of road shapefile
    road_ds.SetGeoTransform((x_min, cellsize, 0, y_max, 0, -cellsize))    # assigns new geotransform
    gdal.RasterizeLayer(road_ds, [1], roads_3035, burn_values=[1],
                        callback=gdal.TermProgress)                       # rasterizes vector data, cells of roads have value 1
    print('road rasters done')

    # creates proximity raster
    prox_ds = tif_driver.Create(root_folder + 'proxi.tif', cols, rows, 1, gdal.GDT_Int32)
    prox_ds.SetProjection(road_ds.GetProjection())
    prox_ds.SetGeoTransform(road_ds.GetGeoTransform())
    gdal.ComputeProximity(road_ds.GetRasterBand(1),                       # calculates proximity to road for each raster cell
                          prox_ds.GetRasterBand(1),
                          ['DISTUNITS=GEO'], gdal.TermProgress)

    print('proximity raster done')

    # create new shapefile
    o_geom = o_feat.geometry()
    data_source = shp_driver.CreateDataSource(root_folder + 'feature.shp')
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    layer = data_source.CreateLayer("feature", srs, ogr.wkbPolygon)
    defn = layer.GetLayerDefn()
    # store one feature (=country) in new shapefile
    feat = ogr.Feature(defn)
    feat.SetGeometry(o_geom)
    layer.CreateFeature(feat)
    print(layer.GetFeatureCount())

    # creates raster of current country to later compute statistics inside country boundary
    co_ds = tif_driver.Create(root_folder + 'tmp.tif', cols, rows)
    co_ds.SetProjection(prox_ds.GetProjection())
    co_ds.SetGeoTransform(prox_ds.GetGeoTransform())
    gdal.RasterizeLayer(co_ds, [1], layer, burn_values=[1],callback=gdal.TermProgress)
    print('country raster done')

    co_data = co_ds.ReadAsArray()                       # reads rasters as array:
    prox_data = prox_ds.ReadAsArray()
    prox_data[co_data == 0] = -99                       # assign no data values outside country boundary
    prox_ds.GetRasterBand(1).WriteArray(prox_data)      # write array back to raster
    prox_ds.GetRasterBand(1).SetNoDataValue(-99)        # declares no data value
    # calculates statistics of raster (minimum, maximum, mean, st.dev):
    stats = prox_ds.GetRasterBand(1).ComputeStatistics(False, gdal.TermProgress)
    roads_list.append([name, round((stats[1]/1000), 2), round((stats[2]/1000), 2)])       # store data in list

    del feat
    roads_3035.SetSpatialFilter(None)
    o_feat = countries_3035_diss.GetNextFeature()


# following code block:
# - gets area for each country, gets length and number of roads per country
area_roads_final = []
counter = 0
for o in countries_3035_diss:
    country_roads = []
    geom_o = o.GetGeometryRef()
    name = o.GetField('state')
    area = geom_o.GetArea()
    roads_3035.SetSpatialFilter(geom_o)                 # set spatial filter on roads layer
    fc = roads_3035.GetFeatureCount()                   # get feature count of filtered layer
    road_feat = roads_3035.GetNextFeature()             # loop through filtered geometries
    while road_feat:
        length = road_feat.GetField('LENGTH_KM')        # get length of each road
        country_roads.append(length)                    # store length value in list
        road_feat = roads_3035.GetNextFeature()
    area_roads_final.append([name, round((area/1000000), 2), fc, sum(country_roads)])  # convert area to km2, store number of roads and length for each country
    roads_3035.SetSpatialFilter(None)

# delete temporary folder with files from disk
try:
    shutil.rmtree(store_folder)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))
print('removed')

# I did not use the reprojected files in the following code because it is not necessary
# (direct coordinate transformation is possible)

# next block of code:
# - loops through dam shapefile and stores necessary information
dam_feature = dams_lyr.GetNextFeature()
df = []
while dam_feature:
    coord = dam_feature.GetGeometryRef()
    coord_cl = coord.Clone()
    coord_cl.Transform(coordTrans)                      # transform coordinate to crs of country layer
    countries_lyr.SetSpatialFilter(coord_cl)            # set spatial filter to select country

    for country in countries_lyr:                       # extract country for dam
        country_name = country.GetField('NAME_0')

    df.append([dam_feature.GetField('DAM_NAME'),        # transfer to nested list
               dam_feature.GetField('YEAR'),
               dam_feature.GetField('AREA_SKM'),
               dam_feature.GetField('DEPTH_M'),
               dam_feature.GetField('ELEV_MASL'),
               dam_feature.GetField('CATCH_SKM'),
               country_name])

    countries_lyr.SetSpatialFilter(None)                # remove spatial filter
    dam_feature = dams_lyr.GetNextFeature()
dams_lyr.ResetReading()

# following code:
# - summarizes data according to task and writes it to csv file

field_names = list(('name', 'year',  'area_skm', 'depth_m', 'elev_masl', 'catch_skm', 'country'))
df_pandas = pd.DataFrame.from_records(df, columns = field_names)

# group dataframe and extract information
## area of the country in km2 //  Kilometers of road per country // Number of roads
area_km2 = pd.DataFrame.from_records(area_roads_final, columns= ['country','area_km2', 'nr_roads', 'roads_km'])

## mean and maximum distance to roads per country
road_dist = pd.DataFrame.from_records(roads_list, columns= ['country','max_road_dist', 'road_dist_km'])

## 1. number of damns per country
nr_dams = df_pandas.groupby(['country'], as_index=False)['country'].agg(['count'])

## 2. year of establishment of oldest dam
yr_old = df_pandas.groupby(['country'], as_index=False)['year'].min()

## 3. name of oldest dam
idx = df_pandas.groupby(['country'])['year'].transform(max) == df_pandas['year']
old_df = df_pandas[idx]
name_old = old_df.drop(['year','area_skm', 'depth_m', 'elev_masl', 'catch_skm'], axis=1)

## 4. year of establishment of youngest dam
yr_young = df_pandas.groupby(['country'],as_index=False)['year'].max()

## 5. name of youngest dam
idx = df_pandas.groupby(['country'])['year'].transform(min) == df_pandas['year']
young_df = df_pandas[idx]
name_young = young_df.drop(['year','area_skm', 'depth_m', 'elev_masl', 'catch_skm'], axis=1)

## 6. average size of reservoir in km2
av_reserv_km2 = df_pandas.groupby(['country'], as_index=False)['area_skm'].mean()

## 7. maximum size of reservoir in km2
max_reserv_km2 = df_pandas.groupby(['country'], as_index=False)['area_skm'].max()

## 8. name of dam with largest reservoir
idx = df_pandas.groupby(['country'])['area_skm'].transform(max) == df_pandas['area_skm']
area_df = df_pandas[idx]
Name_max_reserv = area_df.drop(['year', 'depth_m', 'elev_masl', 'catch_skm', 'area_skm'], axis=1)

## 9. average depth of reservoirs in m
av_depth_reserv_m = df_pandas.groupby(['country'], as_index=False)['depth_m'].mean()

## 10. maximum depth of reservoirs in m
max_depth_reserv_m = df_pandas.groupby(['country'], as_index=False)['depth_m'].max()

## 11. name of dam with deepest reservoir
idx = df_pandas.groupby(['country'])['depth_m'].transform(max) == df_pandas['depth_m']
df1 = df_pandas[idx]
name_max_depth = df1.drop(['year', 'area_skm', 'elev_masl', 'catch_skm', 'depth_m'], axis=1)

## 12. largest catchment in km2
max_catch_km2 = df_pandas.groupby(['country'], as_index=False)['catch_skm'].max()

## 13. name of dam with largest catchment
idx = df_pandas.groupby(['country'])['catch_skm'].transform(max) == df_pandas['catch_skm']
df1 = df_pandas[idx]
Name_max_catch = df1.drop(['year', 'area_skm', 'elev_masl', 'depth_m', 'catch_skm'], axis=1)

# create list of dataframes and merge all to final dataframe
df_fin = [nr_dams,yr_old, name_old, yr_young, name_young, av_reserv_km2, max_reserv_km2, Name_max_reserv, av_depth_reserv_m,
          max_depth_reserv_m, name_max_depth, max_catch_km2, Name_max_catch]
df_final = reduce(lambda left, right: pd.merge(left, right,on='country'), df_fin)

# rename columns
df_final.columns = ['country','nr_dams','yr_old','name_old','yr_young','name_young',
                    'av_reserv_km2','max_reserv_km2','Name_max_depth','av_depth_reserv_m',
                    'max_depth_reserv_m','Name_max_reserv','max_catch_km2','Name_max_catch' ]

# merge with dataframes containing country area, distance values
# use outer join to keep all rows (i.e. countries without dams)
df_final = df_final.merge(area_km2, how='outer', on='country')
df_final = df_final.merge(road_dist, how = 'outer', on='country')

# some dams where built in the same year, however, here I just select the first in alphabetical order and drop the other(s)
df_final.sort_values(by=['country', 'name_old', 'name_young', 'Name_max_depth', 'Name_max_reserv', 'Name_max_catch'])
df_final = df_final.drop_duplicates(subset=['country'], keep = 'first')

# save csv file
df_final.to_csv(path_or_buf= 'Map2.csv', index=False)


########################################################################################################################
# set ending time ######################################################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")